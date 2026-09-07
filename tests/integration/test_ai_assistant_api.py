"""Интеграционные тесты для AI Assistant API."""
import pytest


@pytest.mark.asyncio
class TestAIAssistantAPI:
    async def test_status(self, client):
        r = await client.get("/api/ai/status")
        assert r.status_code == 200
        data = r.json()
        assert data["available"] is False
        assert data["provider"] == "placeholder"
        assert "tg" in data["languages"]

    async def test_chat_returns_reply(self, client):
        r = await client.post("/api/ai/chat", json={
            "message": "Hello", "language": "tg",
        })
        assert r.status_code == 200
        data = r.json()
        assert "reply" in data
        assert len(data["reply"]) > 0
        assert data["provider"] == "placeholder"

    async def test_chat_in_russian(self, client):
        r = await client.post("/api/ai/chat", json={
            "message": "Привет", "language": "ru",
        })
        assert r.status_code == 200
        assert len(r.json()["reply"]) > 0

    async def test_chat_with_default_language(self, client):
        r = await client.post("/api/ai/chat", json={
            "message": "Hello",
        })
        assert r.status_code == 200
