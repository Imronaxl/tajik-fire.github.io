from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Problem,
    ProblemSolve,
    Submission,
    SubmissionFeed,
    TestCase,
    User,
    Verdict,
)
from app.services.judger.languages import get_language_config
from app.services.judger.runner import get_runner
from app.services.judger.verifiers import Verifier


class JudgerService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.runner = get_runner()

    async def judge_submission(self, submission_id: int) -> Dict[str, Any]:
        sub_result = await self.db.execute(select(Submission).where(Submission.id == submission_id))
        submission = sub_result.scalar_one_or_none()
        if submission is None:
            return {"error": "submission not found"}

        problem_result = await self.db.execute(select(Problem).where(Problem.id == submission.problem_id))
        problem = problem_result.scalar_one_or_none()
        if problem is None:
            return {"error": "problem not found"}

        submission.verdict = Verdict.JUDGING
        await self.db.commit()

        lang_config = get_language_config(submission.language)
        if lang_config is None:
            submission.verdict = Verdict.COMPILATION_ERROR
            submission.error_message = f"unsupported language: {submission.language}"
            submission.judged_at = datetime.now(timezone.utc)
            await self.db.commit()
            return {"verdict": "compilation_error", "error": submission.error_message}

        cases_result = await self.db.execute(
            select(TestCase)
            .where(TestCase.problem_id == problem.id)
            .order_by(TestCase.test_order.asc())
        )
        test_cases = list(cases_result.scalars().all())
        if not test_cases:
            submission.verdict = Verdict.RUNTIME_ERROR
            submission.error_message = "no test cases"
            submission.judged_at = datetime.now(timezone.utc)
            await self.db.commit()
            return {"verdict": "runtime_error", "error": "no test cases"}

        total = len(test_cases)
        passed = 0
        peak_time = 0.0
        peak_memory = 0
        verdict = Verdict.ACCEPTED
        error_message: str | None = None

        for idx, test_case in enumerate(test_cases, start=1):
            stdout, stderr, exec_time, memory_used, err = await self.runner.run(
                code=submission.code,
                language=submission.language,
                input_data=test_case.input_data,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit,
            )
            peak_time = max(peak_time, exec_time)
            peak_memory = max(peak_memory, memory_used)

            if err:
                lowered = err.lower()
                if "compilation" in lowered:
                    verdict = Verdict.COMPILATION_ERROR
                    error_message = err
                elif "time limit" in lowered:
                    verdict = Verdict.TIME_LIMIT_EXCEEDED
                    error_message = f"TLE on test {idx}"
                elif "memory" in lowered or "mle" in lowered:
                    verdict = Verdict.MEMORY_LIMIT_EXCEEDED
                    error_message = f"MLE on test {idx}"
                else:
                    verdict = Verdict.RUNTIME_ERROR
                    error_message = f"{err} on test {idx}"
                break

            ok, verify_err = Verifier.compare_outputs(stdout or "", test_case.expected_output)
            if not ok:
                verdict = Verdict.WRONG_ANSWER
                error_message = f"WA on test {idx}"
                if verify_err:
                    error_message += f": {verify_err}"
                break
            passed += 1

        submission.verdict = verdict
        submission.execution_time = round(peak_time, 4)
        submission.memory_used = peak_memory
        submission.test_passed = passed
        submission.test_total = total
        submission.error_message = error_message
        submission.judged_at = datetime.now(timezone.utc)

        if verdict == Verdict.ACCEPTED:
            existing = await self.db.execute(
                select(ProblemSolve).where(
                    ProblemSolve.user_id == submission.user_id,
                    ProblemSolve.problem_id == submission.problem_id,
                )
            )
            if existing.scalar_one_or_none() is None:
                self.db.add(
                    ProblemSolve(
                        user_id=submission.user_id,
                        problem_id=submission.problem_id,
                        submission_id=submission.id,
                        attempts_before_solve=max(0, total - passed),
                    )
                )
                user_result = await self.db.execute(select(User).where(User.id == submission.user_id))
                user = user_result.scalar_one_or_none()
                if user is not None:
                    user.solved_count = (user.solved_count or 0) + 1
                    user.rating = (user.rating or 0) + _rating_gain(problem.difficulty)

        await self.db.commit()

        feed_entry = SubmissionFeed(
            submission_id=submission.id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            verdict=submission.verdict,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
            language=submission.language,
        )
        self.db.add(feed_entry)
        await self.db.commit()

        return {
            "verdict": verdict.value,
            "test_passed": passed,
            "test_total": total,
            "execution_time": submission.execution_time,
            "memory_used": submission.memory_used,
            "error": error_message,
        }


def _rating_gain(difficulty: str) -> int:
    return {"easy": 5, "medium": 12, "hard": 25}.get(difficulty, 5)


async def judge_submission(db: AsyncSession, submission_id: int) -> Dict[str, Any]:
    service = JudgerService(db)
    return await service.judge_submission(submission_id)
