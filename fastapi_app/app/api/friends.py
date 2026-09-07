from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import Friendship, Notification, User
from app.schemas.schemas import FriendshipResponse

router = APIRouter()


def _serialize_friendship(friendship: Friendship, friend: User, current_user: User) -> FriendshipResponse:
    return FriendshipResponse(
        id=friendship.id,
        user_id=current_user.id,
        friend_id=friend.id,
        friend_username=friend.username,
        friend_avatar=friend.avatar_url,
        status=friendship.status,
        created_at=friendship.created_at,
        updated_at=friendship.updated_at,
    )


async def _get_friend(db: AsyncSession, friend_id: int, current_user_id: int) -> User:
    if friend_id == current_user_id:
        raise HTTPException(status_code=400, detail="cannot befriend yourself")
    friend = await db.get(User, friend_id)
    if friend is None:
        raise HTTPException(status_code=404, detail="user not found")
    return friend


@router.post("/request/{friend_id}", response_model=FriendshipResponse)
async def send_friend_request(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    friend = await _get_friend(db, friend_id, current_user.id)

    result = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id),
                (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id),
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="already friends")
        if existing.status == "blocked":
            raise HTTPException(status_code=400, detail="user is blocked")
        if existing.user1_id == current_user.id:
            raise HTTPException(status_code=400, detail="request already sent")

        existing.status = "accepted"
        existing.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing)
        return _serialize_friendship(existing, friend, current_user)

    friendship = Friendship(
        user1_id=current_user.id,
        user2_id=friend_id,
        status="requested",
    )
    db.add(friendship)
    db.add(
        Notification(
            user_id=friend_id,
            title="New friend request",
            message=f"{current_user.username} wants to be your friend",
            notification_type="friendship",
        )
    )
    await db.commit()
    await db.refresh(friendship)
    return _serialize_friendship(friendship, friend, current_user)


@router.delete("/request/{friend_id}")
async def cancel_friend_request(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == current_user.id)
            & (Friendship.user2_id == friend_id)
            & (Friendship.status == "requested")
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=404, detail="request not found")
    await db.delete(friendship)
    await db.commit()
    return {"message": "request cancelled"}


@router.post("/accept/{friend_id}", response_model=FriendshipResponse)
async def accept_friend_request(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == friend_id)
            & (Friendship.user2_id == current_user.id)
            & (Friendship.status == "requested")
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=404, detail="request not found")

    friendship.status = "accepted"
    friendship.updated_at = datetime.now(timezone.utc)
    db.add(
        Notification(
            user_id=friend_id,
            title="Friend request accepted",
            message=f"{current_user.username} accepted your request",
            notification_type="friendship",
        )
    )
    await db.commit()
    await db.refresh(friendship)
    friend = await db.get(User, friend_id)
    return _serialize_friendship(friendship, friend, current_user)


@router.post("/reject/{friend_id}")
async def reject_friend_request(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            (Friendship.user1_id == friend_id)
            & (Friendship.user2_id == current_user.id)
            & (Friendship.status == "requested")
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=404, detail="request not found")
    await db.delete(friendship)
    await db.commit()
    return {"message": "request rejected"}


@router.delete("/{friend_id}")
async def remove_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user1_id == current_user.id) & (Friendship.user2_id == friend_id),
                (Friendship.user1_id == friend_id) & (Friendship.user2_id == current_user.id),
            )
            & (Friendship.status == "accepted")
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=404, detail="friendship not found")
    await db.delete(friendship)
    await db.commit()
    return {"message": "friend removed"}


@router.get("/list", response_model=List[FriendshipResponse])
async def list_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            (
                (Friendship.user1_id == current_user.id)
                | (Friendship.user2_id == current_user.id)
            )
            & (Friendship.status == "accepted")
        )
    )
    friendships = result.scalars().all()

    out = []
    for friendship in friendships:
        friend_id = friendship.user2_id if friendship.user1_id == current_user.id else friendship.user1_id
        friend = await db.get(User, friend_id)
        if friend is not None:
            out.append(_serialize_friendship(friendship, friend, current_user))
    return out


@router.get("/requests", response_model=List[FriendshipResponse])
async def list_friend_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Friendship).where(
            (Friendship.user2_id == current_user.id) & (Friendship.status == "requested")
        )
    )
    friendships = result.scalars().all()

    out = []
    for friendship in friendships:
        requester = await db.get(User, friendship.user1_id)
        if requester is not None:
            out.append(_serialize_friendship(friendship, requester, current_user))
    return out
