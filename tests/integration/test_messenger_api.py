"""Интеграционные тесты для Messenger API."""
import pytest


@pytest.mark.asyncio
class TestMessengerAPI:
    async def test_list_chats_unauthorized(self, client):
        r = await client.get("/api/messenger/chats")
        assert r.status_code == 401

    async def test_list_chats_empty(self, client, auth_headers):
        r = await client.get("/api/messenger/chats", headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == []

    async def test_create_direct_chat_invalid(self, client, auth_headers):
        r = await client.post("/api/messenger/chats", json={
            "is_group": False, "member_ids": [],
        }, headers=auth_headers)
        assert r.status_code == 400

    async def test_send_message_no_target(self, client, auth_headers):
        r = await client.post("/api/messenger/messages", json={
            "content": "hello",
        }, headers=auth_headers)
        assert r.status_code == 400

    async def test_send_message_to_unknown_receiver(self, client, auth_headers):
        r = await client.post("/api/messenger/messages", json={
            "content": "hello", "receiver_id": 99999,
        }, headers=auth_headers)
        assert r.status_code == 404

    async def test_online_users(self, client, auth_headers):
        r = await client.get("/api/messenger/online", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
