"""Интеграционные тесты для Tasks API."""
import pytest


@pytest.mark.asyncio
class TestTasksAPI:
    async def test_list_tasks_unauthorized(self, client):
        r = await client.get("/api/tasks/")
        assert r.status_code == 401

    async def test_create_task(self, client, auth_headers):
        r = await client.post("/api/tasks/", json={
            "title": "Test task",
            "description": "test",
            "status": "todo",
            "priority": "high",
        }, headers=auth_headers)
        assert r.status_code == 201
        assert r.json()["title"] == "Test task"
        assert r.json()["priority"] == "high"

    async def test_list_tasks(self, client, auth_headers):
        await client.post("/api/tasks/", json={"title": "T1"}, headers=auth_headers)
        await client.post("/api/tasks/", json={"title": "T2"}, headers=auth_headers)
        r = await client.get("/api/tasks/", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 2

    async def test_update_task(self, client, auth_headers):
        r = await client.post("/api/tasks/", json={"title": "To update"}, headers=auth_headers)
        task_id = r.json()["id"]
        r = await client.patch(f"/api/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["status"] == "done"

    async def test_delete_task(self, client, auth_headers):
        r = await client.post("/api/tasks/", json={"title": "To delete"}, headers=auth_headers)
        task_id = r.json()["id"]
        r = await client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert r.status_code == 200
        r = await client.get("/api/tasks/", headers=auth_headers)
        assert all(t["id"] != task_id for t in r.json())

    async def test_get_nonexistent_task(self, client, auth_headers):
        r = await client.patch("/api/tasks/99999", json={"status": "done"}, headers=auth_headers)
        assert r.status_code == 404
