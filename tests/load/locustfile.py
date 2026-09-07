"""Нагрузочные тесты через Locust.

Запуск:
    cd fastapi_app && uvicorn main:app --reload &
    cd tests/load && locust -f locustfile.py --host=http://localhost:8000

Откройте http://localhost:8089 для настройки количества пользователей и RPS.
"""
from locust import HttpUser, task, between


class TajikFireUser(HttpUser):
    wait_time = between(1, 3)
    weight = 1

    @task(3)
    def browse_home(self):
        self.client.get("/")

    @task(2)
    def browse_problems(self):
        self.client.get("/api/problems/?limit=20")

    @task(2)
    def view_dashboard(self):
        self.client.get("/api/stats/dashboard")

    @task(1)
    def view_leaderboard(self):
        self.client.get("/api/stats/leaderboard")

    @task(1)
    def view_feed(self):
        self.client.get("/api/stats/feed?limit=20")

    @task(1)
    def view_learning(self):
        self.client.get("/api/learning/modules")


class AuthenticatedUser(HttpUser):
    wait_time = between(2, 5)
    weight = 1

    def on_start(self):
        r = self.client.post("/api/auth/login", json={
            "login": "demo",
            "password": "Demo1234",
        })
        if r.status_code == 200:
            token = r.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task(2)
    def list_tasks(self):
        self.client.get("/api/tasks/", headers=self.headers)

    @task(1)
    def list_chats(self):
        self.client.get("/api/messenger/chats", headers=self.headers)

    @task(1)
    def my_stats(self):
        self.client.get("/api/stats/me", headers=self.headers)
