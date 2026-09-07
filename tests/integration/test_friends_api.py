"""Интеграционные тесты для Friends API."""
import pytest


@pytest.mark.asyncio
class TestFriendsAPI:
    async def test_list_friends_unauthorized(self, client):
        r = await client.get("/api/friends/list")
        assert r.status_code == 401

    async def test_list_friends_empty(self, client, auth_headers):
        r = await client.get("/api/friends/list", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == []

    async def test_list_requests_empty(self, client, auth_headers):
        r = await client.get("/api/friends/requests", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == []

    async def test_send_request_to_self(self, client, auth_headers, auth_token):
        from jose import jwt
        from app.core.config import settings
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = 1
        r = await client.post(f"/api/friends/request/{user_id}", headers=auth_headers)
        assert r.status_code == 400

    async def test_send_request_to_nonexistent(self, client, auth_headers):
        r = await client.post("/api/friends/request/99999", headers=auth_headers)
        assert r.status_code == 404
