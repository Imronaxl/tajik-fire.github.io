from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import Chat, ChatMember, Message, User
from app.schemas.schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse

router = APIRouter()


async def _ensure_chat_member(db: AsyncSession, chat_id: int, user_id: int) -> Chat:
    result = await db.execute(
        select(Chat)
        .options(selectinload(Chat.members).selectinload(ChatMember.user))
        .where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not found")
    if not any(m.user_id == user_id for m in chat.members):
        raise HTTPException(status_code=403, detail="not a chat member")
    return chat


@router.get("/chats", response_model=List[ChatResponse])
async def list_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chat)
        .join(ChatMember)
        .options(
            selectinload(Chat.members).selectinload(ChatMember.user),
            selectinload(Chat.messages),
        )
        .where(ChatMember.user_id == current_user.id)
        .order_by(desc(Chat.updated_at))
    )
    chats = result.scalars().unique().all()

    response = []
    for chat in chats:
        last_message_result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_message = last_message_result.scalar_one_or_none()

        unread_result = await db.execute(
            select(func.count(Message.id))
            .where(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id,
                Message.is_read.is_(False),
            )
        )
        unread = unread_result.scalar() or 0

        members = [m.user for m in chat.members if m.user is not None]
        response.append(
            ChatResponse(
                id=chat.id,
                name=chat.name,
                is_group=chat.is_group,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                members=members,
                last_message=last_message,
                unread_count=unread,
            )
        )
    return response


@router.post("/chats", response_model=ChatResponse, status_code=201)
async def create_chat(
    payload: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member_ids = list({*payload.member_ids, current_user.id})
    if not payload.is_group and len(member_ids) != 2:
        raise HTTPException(status_code=400, detail="direct chat requires exactly one other member")

    chat = Chat(name=payload.name if payload.is_group else None, is_group=payload.is_group)
    db.add(chat)
    await db.flush()

    for uid in member_ids:
        user = await db.get(User, uid)
        if user is None:
            raise HTTPException(status_code=404, detail=f"user {uid} not found")
        db.add(ChatMember(chat_id=chat.id, user_id=uid))

    await db.commit()
    await db.refresh(chat)

    members_result = await db.execute(
        select(User)
        .join(ChatMember, ChatMember.user_id == User.id)
        .where(ChatMember.chat_id == chat.id)
    )
    members = list(members_result.scalars().all())

    return ChatResponse(
        id=chat.id,
        name=chat.name,
        is_group=chat.is_group,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        members=members,
        last_message=None,
        unread_count=0,
    )


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def list_chat_messages(
    chat_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _ensure_chat_member(db, chat_id, current_user.id)
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = list(result.scalars().all())

    await db.execute(
        Message.__table__.update()
        .where(
            Message.chat_id == chat_id,
            Message.sender_id != current_user.id,
            Message.is_read.is_(False),
        )
        .values(is_read=True)
    )
    await db.commit()
    return messages


@router.post("/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not payload.chat_id and not payload.receiver_id:
        raise HTTPException(status_code=400, detail="chat_id or receiver_id required")

    if payload.chat_id:
        await _ensure_chat_member(db, payload.chat_id, current_user.id)
        message = Message(
            content=payload.content,
            sender_id=current_user.id,
            chat_id=payload.chat_id,
        )
        await db.execute(
            Chat.__table__.update()
            .where(Chat.id == payload.chat_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
    else:
        receiver = await db.get(User, payload.receiver_id)
        if receiver is None:
            raise HTTPException(status_code=404, detail="receiver not found")
        message = Message(
            content=payload.content,
            sender_id=current_user.id,
            receiver_id=payload.receiver_id,
        )

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/messages/direct/{user_id}", response_model=List[MessageResponse])
async def list_direct_messages(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="cannot message yourself")

    result = await db.execute(
        select(Message)
        .where(
            (
                ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id))
                | ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
            )
            & (Message.chat_id.is_(None))
        )
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    messages = list(result.scalars().all())

    await db.execute(
        Message.__table__.update()
        .where(
            (Message.sender_id == user_id)
            & (Message.receiver_id == current_user.id)
            & (Message.is_read.is_(False))
        )
        .values(is_read=True)
    )
    await db.commit()
    return messages


@router.patch("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    message = await db.get(Message, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="message not found")
    message.is_read = True
    await db.commit()
    return {"message": "marked as read"}


@router.get("/online")
async def list_online_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.is_active.is_(True)).limit(50)
    )
    users = result.scalars().all()
    return [
        {"id": u.id, "username": u.username, "avatar_url": u.avatar_url}
        for u in users
    ]
