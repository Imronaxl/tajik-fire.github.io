"""Интеграционные тесты для судьи — упрощённые."""
import asyncio

import pytest


@pytest.mark.asyncio
class TestJudgerPipeline:
    async def test_submit_returns_pending(self, client, auth_headers, db_session):
        from app.models.models import Problem, TestCase, Language, ProblemTranslation
        problem = Problem(
            title="A + B", difficulty="easy", time_limit=2.0,
            memory_limit=256, is_published=True, category="math",
        )
        db_session.add(problem)
        await db_session.flush()
        db_session.add(ProblemTranslation(
            problem_id=problem.id, language=Language.EN,
            title="A+B", statement="sum", input_format="two ints", output_format="sum",
        ))
        db_session.add(TestCase(
            problem_id=problem.id, test_order=1,
            input_data="2 3\n", expected_output="5\n", is_sample=True,
        ))
        await db_session.commit()

        r = await client.post("/api/problems/submissions", headers=auth_headers, json={
            "problem_id": problem.id, "language": "python3",
            "code": "a, b = map(int, input().split()); print(a + b)",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["verdict"] in ("pending", "judging", "accepted")
        assert data["problem_id"] == problem.id

    async def test_submit_to_nonexistent_problem(self, client, auth_headers):
        r = await client.post("/api/problems/submissions", headers=auth_headers, json={
            "problem_id": 99999, "language": "python3",
            "code": "print(1)",
        })
        assert r.status_code == 404

    async def test_submit_to_unpublished_problem(self, client, auth_headers, db_session):
        from app.models.models import Problem
        problem = Problem(
            title="Hidden", difficulty="easy", time_limit=2.0,
            memory_limit=256, is_published=False, category="math",
        )
        db_session.add(problem)
        await db_session.commit()

        r = await client.post("/api/problems/submissions", headers=auth_headers, json={
            "problem_id": problem.id, "language": "python3",
            "code": "print(1)",
        })
        assert r.status_code == 403

    async def test_get_submission_status(self, client, auth_headers, db_session):
        from app.models.models import Problem, TestCase, Language, ProblemTranslation, Submission, Verdict, ProgrammingLanguage
        from datetime import datetime, timezone
        problem = Problem(
            title="A + B", difficulty="easy", time_limit=2.0,
            memory_limit=256, is_published=True, category="math",
        )
        db_session.add(problem)
        await db_session.flush()
        db_session.add(ProblemTranslation(
            problem_id=problem.id, language=Language.EN,
            title="A+B", statement="sum", input_format="two ints", output_format="sum",
        ))
        await db_session.commit()

        from app.models.models import User
        from sqlalchemy import select
        result = await db_session.execute(select(User).where(User.username == "testuser"))
        user = result.scalar_one()
        submission = Submission(
            user_id=user.id, problem_id=problem.id,
            code="print(1)", language=ProgrammingLanguage.PYTHON3,
            verdict=Verdict.ACCEPTED, test_passed=1, test_total=1,
            execution_time=0.05, judged_at=datetime.now(timezone.utc),
        )
        db_session.add(submission)
        await db_session.commit()

        r = await client.get(f"/api/problems/submissions/{submission.id}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["verdict"] == "accepted"
