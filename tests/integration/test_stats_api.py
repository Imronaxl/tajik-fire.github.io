"""Интеграционные тесты для Stats API."""
import pytest


@pytest.mark.asyncio
class TestStatsAPI:
    async def test_dashboard(self, client):
        r = await client.get("/api/stats/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert "total_users" in data
        assert "total_problems" in data
        assert "total_submissions" in data
        assert "accepted_rate" in data
        assert "recent_feed" in data
        assert "top_users" in data

    async def test_leaderboard(self, client):
        r = await client.get("/api/stats/leaderboard")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_feed(self, client):
        r = await client.get("/api/stats/feed")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_me_unauthorized(self, client):
        r = await client.get("/api/stats/me")
        assert r.status_code == 200
        assert r.json()["authenticated"] is False

    async def test_me_authorized(self, client, auth_headers):
        r = await client.get("/api/stats/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["authenticated"] is True
        assert data["username"] == "testuser"
