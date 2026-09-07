from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.db.database import AsyncSessionLocal, get_db
from app.models.models import (
    Problem,
    ProblemSolve,
    ProblemTranslation,
    ProgrammingLanguage,
    Submission,
    TestCase,
    User,
    Verdict,
)
from app.schemas.schemas import (
    ProblemCreate,
    ProblemDetailResponse,
    ProblemResponse,
    ProblemUpdate,
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.judger.judger import judge_submission

router = APIRouter()


async def _attach_solved_count(db: AsyncSession, problems: List[Problem]) -> dict[int, int]:
    if not problems:
        return {}
    ids = [p.id for p in problems]
    result = await db.execute(
        select(ProblemSolve.problem_id, func.count(ProblemSolve.user_id))
        .where(ProblemSolve.problem_id.in_(ids))
        .group_by(ProblemSolve.problem_id)
    )
    return dict(result.all())


@router.get("/", response_model=List[ProblemResponse])
async def list_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Problem).where(Problem.is_published.is_(True))
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    if category:
        stmt = stmt.where(Problem.category == category)
    if search:
        stmt = stmt.where(Problem.title.ilike(f"%{search}%"))
    stmt = stmt.order_by(Problem.id.asc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    problems = list(result.scalars().all())
    solves_map = await _attach_solved_count(db, problems)

    return [
        ProblemResponse(
            id=p.id,
            title=p.title,
            difficulty=p.difficulty,
            time_limit=p.time_limit,
            memory_limit=p.memory_limit,
            is_published=p.is_published,
            author_id=p.author_id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            category=p.category,
            solved_count=solves_map.get(p.id, 0),
            translations=[],
            test_cases=[],
        )
        for p in problems
    ]


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Problem.category, func.count(Problem.id))
        .where(Problem.is_published.is_(True))
        .group_by(Problem.category)
    )
    return [{"name": name or "uncategorized", "count": count} for name, count in result.all()]


@router.get("/{problem_id}", response_model=ProblemDetailResponse)
async def get_problem(
    problem_id: int,
    lang: str = Query("en", pattern="^(tj|ru|en)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if problem is None:
        raise HTTPException(status_code=404, detail="problem not found")
    if not problem.is_published:
        raise HTTPException(status_code=403, detail="problem is not published")

    translation = None
    t_result = await db.execute(
        select(ProblemTranslation).where(
            ProblemTranslation.problem_id == problem.id,
            ProblemTranslation.language == lang,
        )
    )
    translation = t_result.scalar_one_or_none()

    samples_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem.id, TestCase.is_sample.is_(True))
        .order_by(TestCase.test_order.asc())
    )
    samples = list(samples_result.scalars().all())

    solves_result = await db.execute(
        select(func.count(ProblemSolve.user_id))
        .where(ProblemSolve.problem_id == problem.id)
    )
    solved_count = solves_result.scalar() or 0

    return ProblemDetailResponse(
        id=problem.id,
        title=translation.title if translation else problem.title,
        difficulty=problem.difficulty,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        is_published=problem.is_published,
        author_id=problem.author_id,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        category=problem.category,
        solved_count=solved_count,
        translations=[],
        test_cases=[],
        statement=translation.statement if translation else "",
        input_format=translation.input_format if translation else "",
        output_format=translation.output_format if translation else "",
        notes=translation.notes if translation else "",
        language=lang,
    )


@router.post("/", response_model=ProblemResponse, status_code=201)
async def create_problem(
    payload: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem = Problem(
        title=payload.title,
        difficulty=payload.difficulty,
        time_limit=payload.time_limit,
        memory_limit=payload.memory_limit,
        category=payload.category,
        author_id=current_user.id,
        is_published=False,
    )
    db.add(problem)
    await db.flush()

    for trans in payload.translations:
        db.add(
            ProblemTranslation(
                problem_id=problem.id,
                language=trans.language,
                title=trans.title,
                statement=trans.statement,
                input_format=trans.input_format,
                output_format=trans.output_format,
                notes=trans.notes,
            )
        )
    for test in payload.test_cases:
        db.add(
            TestCase(
                problem_id=problem.id,
                test_order=test.test_order,
                input_data=test.input_data,
                expected_output=test.expected_output,
                is_sample=test.is_sample,
            )
        )
    await db.commit()
    await db.refresh(problem)

    return ProblemResponse(
        id=problem.id,
        title=problem.title,
        difficulty=problem.difficulty,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        is_published=problem.is_published,
        author_id=problem.author_id,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        category=problem.category,
        solved_count=0,
        translations=[],
        test_cases=[],
    )


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    payload: ProblemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if problem is None:
        raise HTTPException(status_code=404, detail="problem not found")
    if problem.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(problem, field, value)
    problem.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(problem)

    solves_result = await db.execute(
        select(func.count(ProblemSolve.user_id))
        .where(ProblemSolve.problem_id == problem.id)
    )
    solved_count = solves_result.scalar() or 0

    return ProblemResponse(
        id=problem.id,
        title=problem.title,
        difficulty=problem.difficulty,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        is_published=problem.is_published,
        author_id=problem.author_id,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        category=problem.category,
        solved_count=solved_count,
        translations=[],
        test_cases=[],
    )


@router.post("/submissions", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    problem_result = await db.execute(select(Problem).where(Problem.id == payload.problem_id))
    problem = problem_result.scalar_one_or_none()
    if problem is None:
        raise HTTPException(status_code=404, detail="problem not found")
    if not problem.is_published:
        raise HTTPException(status_code=403, detail="problem is not published")

    submission = Submission(
        user_id=current_user.id,
        problem_id=payload.problem_id,
        code=payload.code,
        language=payload.language,
        verdict=Verdict.PENDING,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    current_user.attempt_count = (current_user.attempt_count or 0) + 1
    await db.commit()

    import asyncio
    asyncio.create_task(_judge_in_background(submission.id))

    return submission


async def _judge_in_background(submission_id: int) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await judge_submission(session, submission_id)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("judging %s failed: %s", submission_id, exc)

@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=404, detail="submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized")
    return submission


@router.get("/submissions", response_model=List[SubmissionResponse])
async def list_submissions(
    problem_id: Optional[int] = None,
    user_id: Optional[int] = None,
    verdict: Optional[str] = None,
    language: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Submission)
    if problem_id:
        stmt = stmt.where(Submission.problem_id == problem_id)
    if user_id:
        stmt = stmt.where(Submission.user_id == user_id)
    if verdict:
        stmt = stmt.where(Submission.verdict == verdict)
    if language:
        stmt = stmt.where(Submission.language == language)
    stmt = stmt.order_by(desc(Submission.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{problem_id}/status")
async def get_problem_status(
    problem_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    solve_result = await db.execute(
        select(ProblemSolve).where(
            ProblemSolve.problem_id == problem_id,
            ProblemSolve.user_id == current_user.id,
        )
    )
    solve = solve_result.scalar_one_or_none()
    if solve is not None:
        return {"solved": True, "solved_at": solve.solved_at, "attempts": solve.attempts_before_solve}

    attempts_result = await db.execute(
        select(func.count(Submission.id)).where(
            Submission.problem_id == problem_id,
            Submission.user_id == current_user.id,
        )
    )
    attempts = attempts_result.scalar() or 0
    return {"solved": False, "attempts": attempts}
