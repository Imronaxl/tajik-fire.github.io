from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import Contest, ContestParticipation, User
from app.schemas.schemas import ContestResponse

router = APIRouter()


@router.get("/contests", response_model=List[ContestResponse])
async def list_contests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Contest)
        .where(Contest.is_published.is_(True))
        .order_by(desc(Contest.start_time))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/contests/{contest_id}", response_model=ContestResponse)
async def get_contest(contest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    if contest is None:
        raise HTTPException(status_code=404, detail="contest not found")
    return contest


@router.get("/contests/{contest_id}/standings")
async def get_contest_standings(contest_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    if contest is None:
        raise HTTPException(status_code=404, detail="contest not found")

    parts_result = await db.execute(
        select(ContestParticipation, User)
        .join(User, ContestParticipation.user_id == User.id)
        .where(ContestParticipation.contest_id == contest_id)
        .order_by(ContestParticipation.score.desc(), ContestParticipation.penalty.asc())
    )
    standings = []
    for idx, (participation, user) in enumerate(parts_result.all(), start=1):
        standings.append({
            "rank": idx,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "score": participation.score,
            "penalty": participation.penalty,
        })
    return {"contest_id": contest.id, "title": contest.title, "standings": standings}
