"""Интеграционные тесты для Auth API."""
import pytest


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_register_invalid_password(self, client):
        r = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "weak",
        })
        assert r.status_code in (400, 422)

    async def test_register_short_username(self, client):
        r = await client.post("/api/auth/register", json={
            "username": "ab",
            "email": "new@example.com",
            "password": "Test1234",
        })
        assert r.status_code == 422

    async def test_register_valid_user(self, client):
        r = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Test1234",
            "first_name": "New",
            "last_name": "User",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data

    async def test_register_duplicate(self, client, demo_user_payload):
        await client.post("/api/auth/register", json=demo_user_payload)
        r = await client.post("/api/auth/register", json=demo_user_payload)
        assert r.status_code == 409

    async def test_login_correct(self, client, auth_headers):
        assert auth_headers["Authorization"].startswith("Bearer ")

    async def test_login_wrong_password(self, client, demo_user_payload):
        await client.post("/api/auth/register", json=demo_user_payload)
        r = await client.post("/api/auth/login", json={
            "login": demo_user_payload["username"],
            "password": "wrongpass",
        })
        assert r.status_code == 401

    async def test_me_without_token(self, client):
        r = await client.get("/api/auth/me")
        assert r.status_code == 401

    async def test_me_with_token(self, client, auth_headers):
        r = await client.get("/api/auth/me", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "testuser"

    async def test_refresh_with_invalid_token(self, client):
        r = await client.post("/api/auth/refresh", json={"refresh_token": "invalid"})
        assert r.status_code == 401

    async def test_logout(self, client, auth_headers):
        r = await client.post("/api/auth/logout", headers=auth_headers)
        assert r.status_code == 200

    async def test_reset_password_request_unknown_email(self, client):
        r = await client.post("/api/auth/reset-password-request", json={"email": "nonexistent@example.com"})
        assert r.status_code == 200
        assert "if the email exists" in r.json()["message"].lower()
