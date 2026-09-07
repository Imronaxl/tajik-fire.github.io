"""Интеграционные тесты для Problems API."""
import pytest


@pytest.mark.asyncio
class TestProblemsAPI:
    async def test_list_problems_empty(self, client):
        r = await client.get("/api/problems/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_list_problems_with_pagination(self, client):
        r = await client.get("/api/problems/?skip=0&limit=5")
        assert r.status_code == 200

    async def test_list_problems_with_filters(self, client):
        r = await client.get("/api/problems/?difficulty=easy&category=math")
        assert r.status_code == 200

    async def test_get_problem_not_found(self, client):
        r = await client.get("/api/problems/99999")
        assert r.status_code == 404

    async def test_get_problem_with_lang(self, client, db_session):
        from app.models.models import Problem, ProblemTranslation, TestCase, Language
        problem = Problem(title="Test", difficulty="easy", time_limit=1.0, memory_limit=256, is_published=True, category="test")
        db_session.add(problem)
        await db_session.flush()
        db_session.add(ProblemTranslation(
            problem_id=problem.id, language=Language.EN, title="Test",
            statement="Test statement", input_format="in", output_format="out",
        ))
        db_session.add(TestCase(
            problem_id=problem.id, test_order=1, input_data="1\n", expected_output="1\n", is_sample=True,
        ))
        await db_session.commit()

        r = await client.get(f"/api/problems/{problem.id}?lang=en")
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Test"
        assert "Test statement" in data["statement"]

    async def test_categories_endpoint(self, client):
        r = await client.get("/api/problems/categories")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_submit_unauthorized(self, client):
        r = await client.post("/api/problems/submissions", json={
            "problem_id": 1, "language": "python3", "code": "print(1)",
        })
        assert r.status_code == 401

    async def test_submissions_list_unauthorized(self, client):
        r = await client.get("/api/problems/submissions/")
        assert r.status_code in (401, 200)
