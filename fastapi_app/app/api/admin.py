from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import User

router = APIRouter()


def _is_admin(user: User) -> bool:
    return bool(user and user.is_active and user.id == 1)


@router.get("/users")
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise HTTPException(status_code=403, detail="admin access required")
    result = await db.execute(
        select(User).order_by(User.id.asc()).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "rating": u.rating,
            "solved_count": u.solved_count,
            "created_at": u.created_at,
        }
        for u in users
    ]
