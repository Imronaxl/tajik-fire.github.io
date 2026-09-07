from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_optional
from app.db.database import get_db
from app.models.models import (
    Problem,
    ProblemSolve,
    Submission,
    SubmissionFeed,
    User,
    Verdict,
)

router = APIRouter()


@router.get("/stats/dashboard")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.scalar(select(func.count(User.id)))
    total_problems = await db.scalar(
        select(func.count(Problem.id)).where(Problem.is_published.is_(True))
    )
    total_submissions = await db.scalar(select(func.count(Submission.id)))
    total_solved = await db.scalar(select(func.count(ProblemSolve.id)))

    accepted = await db.scalar(
        select(func.count(Submission.id)).where(Submission.verdict == Verdict.ACCEPTED)
    )
    accepted_rate = (accepted / total_submissions * 100.0) if total_submissions else 0.0

    feed_result = await db.execute(
        select(SubmissionFeed, User, Problem)
        .join(User, SubmissionFeed.user_id == User.id)
        .join(Problem, SubmissionFeed.problem_id == Problem.id)
        .order_by(desc(SubmissionFeed.created_at))
        .limit(15)
    )
    recent_feed = [
        {
            "id": feed.id,
            "submission_id": feed.submission_id,
            "user_id": feed.user_id,
            "username": user.username,
            "problem_id": feed.problem_id,
            "problem_title": problem.title,
            "verdict": feed.verdict.value,
            "execution_time": feed.execution_time,
            "memory_used": feed.memory_used,
            "language": feed.language.value,
            "created_at": feed.created_at,
        }
        for feed, user, problem in feed_result.all()
    ]

    top_result = await db.execute(
        select(User)
        .order_by(desc(User.rating))
        .limit(10)
    )
    top_users = [
        {
            "rank": idx,
            "user_id": u.id,
            "username": u.username,
            "avatar_url": u.avatar_url,
            "rating": u.rating,
            "solved_count": u.solved_count,
            "attempt_count": u.attempt_count,
        }
        for idx, u in enumerate(top_result.scalars().all(), start=1)
    ]

    return {
        "total_users": total_users,
        "total_problems": total_problems,
        "total_submissions": total_submissions,
        "total_solved": total_solved,
        "accepted_rate": round(accepted_rate, 2),
        "recent_feed": recent_feed,
        "top_users": top_users,
    }


@router.get("/stats/leaderboard")
async def leaderboard(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.is_active.is_(True))
        .order_by(desc(User.rating), desc(User.solved_count))
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return [
        {
            "rank": skip + idx,
            "user_id": u.id,
            "username": u.username,
            "avatar_url": u.avatar_url,
            "rating": u.rating,
            "solved_count": u.solved_count,
            "attempt_count": u.attempt_count,
        }
        for idx, u in enumerate(users, start=1)
    ]


@router.get("/stats/feed")
async def submission_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SubmissionFeed, User, Problem)
        .join(User, SubmissionFeed.user_id == User.id)
        .join(Problem, SubmissionFeed.problem_id == Problem.id)
        .order_by(desc(SubmissionFeed.created_at))
        .offset(skip)
        .limit(limit)
    )
    return [
        {
            "id": feed.id,
            "submission_id": feed.submission_id,
            "user_id": feed.user_id,
            "username": user.username,
            "problem_id": feed.problem_id,
            "problem_title": problem.title,
            "verdict": feed.verdict.value,
            "execution_time": feed.execution_time,
            "memory_used": feed.memory_used,
            "language": feed.language.value,
            "created_at": feed.created_at,
        }
        for feed, user, problem in result.all()
    ]


@router.get("/stats/me")
async def my_stats(
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if current_user is None:
        return {"authenticated": False}

    submissions_count = await db.scalar(
        select(func.count(Submission.id)).where(Submission.user_id == current_user.id)
    )
    accepted_count = await db.scalar(
        select(func.count(Submission.id)).where(
            Submission.user_id == current_user.id,
            Submission.verdict == Verdict.ACCEPTED,
        )
    )
    solved = await db.scalar(
        select(func.count(ProblemSolve.id)).where(ProblemSolve.user_id == current_user.id)
    )

    return {
        "authenticated": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "rating": current_user.rating,
        "solved_count": current_user.solved_count,
        "attempt_count": current_user.attempt_count,
        "submissions_count": submissions_count,
        "accepted_count": accepted_count,
        "success_rate": (accepted_count / submissions_count * 100.0) if submissions_count else 0.0,
    }
