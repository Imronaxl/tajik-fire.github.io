from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import User

router = APIRouter()


@router.get("/search", response_model=List[dict])
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not q or len(q) < 2:
        return []
    result = await db.execute(
        select(User)
        .where(
            (
                User.username.ilike(f"%{q}%")
                | User.email.ilike(f"%{q}%")
                | User.first_name.ilike(f"%{q}%")
                | User.last_name.ilike(f"%{q}%")
            )
            & (User.id != current_user.id)
            & (User.is_active.is_(True))
        )
        .limit(10)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "avatar_url": u.avatar_url,
            "rating": u.rating,
            "solved_count": u.solved_count,
        }
        for u in users
    ]


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar_url": user.avatar_url,
        "rating": user.rating,
        "solved_count": user.solved_count,
        "attempt_count": user.attempt_count,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
    }
