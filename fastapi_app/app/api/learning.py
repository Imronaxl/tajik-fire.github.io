from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import (
    LearningEnrollment,
    LearningModule,
    LearningProblem,
    Problem,
    User,
)

router = APIRouter()


@router.get("/modules")
async def list_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningModule)
        .where(LearningModule.is_published.is_(True))
        .order_by(LearningModule.order.asc())
        .offset(skip)
        .limit(limit)
    )
    modules = result.scalars().all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "slug": m.slug,
            "description": m.description,
            "order": m.order,
            "theory_excerpt": (m.theory_content or "")[:280],
        }
        for m in modules
    ]


@router.get("/modules/{slug}")
async def get_module(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LearningModule).where(LearningModule.slug == slug))
    module = result.scalar_one_or_none()
    if module is None:
        raise HTTPException(status_code=404, detail="module not found")

    problems_result = await db.execute(
        select(LearningProblem, Problem)
        .join(Problem, LearningProblem.problem_id == Problem.id)
        .where(LearningProblem.module_id == module.id)
        .order_by(LearningProblem.order.asc())
    )
    problems = [
        {
            "id": problem.id,
            "order": lp.order,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "category": problem.category,
        }
        for lp, problem in problems_result.all()
    ]

    enrollment_result = await db.execute(
        select(LearningEnrollment).where(
            LearningEnrollment.module_id == module.id,
            LearningEnrollment.user_id == current_user.id,
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()

    return {
        "id": module.id,
        "title": module.title,
        "slug": module.slug,
        "description": module.description,
        "theory_content": module.theory_content,
        "order": module.order,
        "problems": problems,
        "enrolled": enrollment is not None,
        "progress": enrollment.progress if enrollment else 0,
    }


@router.post("/modules/{module_id}/enroll")
async def enroll_in_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    module = await db.get(LearningModule, module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="module not found")

    existing = await db.execute(
        select(LearningEnrollment).where(
            LearningEnrollment.module_id == module_id,
            LearningEnrollment.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return {"message": "already enrolled"}

    db.add(LearningEnrollment(user_id=current_user.id, module_id=module_id, progress=0))
    await db.commit()
    return {"message": "enrolled"}


@router.get("/my-modules")
async def list_my_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningEnrollment, LearningModule)
        .join(LearningModule, LearningEnrollment.module_id == LearningModule.id)
        .where(LearningEnrollment.user_id == current_user.id)
        .order_by(LearningEnrollment.enrolled_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": module.id,
            "title": module.title,
            "slug": module.slug,
            "description": module.description,
            "progress": enrollment.progress,
            "completed_at": enrollment.completed_at,
            "enrolled_at": enrollment.enrolled_at,
        }
        for enrollment, module in rows
    ]
