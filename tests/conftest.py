"""
Конфигурация тестов tajik-fire.

Запуск всех тестов:
    pytest tests/ -v

Запуск только unit-тестов:
    pytest tests/unit/ -v

Запуск только integration-тестов:
    pytest tests/integration/ -v
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "fastapi_app"))

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(_create_all_tables)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(_drop_all_tables)


def _create_all_tables(conn):
    from app.db.database import Base
    from app.models import (  # noqa: F401 register models on Base.metadata
        User, Chat, ChatMember, Message, Task,
        Problem, ProblemTranslation, TestCase, Submission,
        ProblemSolve, Contest, ContestProblem, ContestParticipation,
        Rating, Friendship, Notification, BlockedUser,
        LearningModule, LearningProblem, LearningEnrollment,
        SubmissionFeed, News, EmailCode, LoginAttempt, AuthToken, TempUser,
    )
    Base.metadata.create_all(conn)


def _drop_all_tables(conn):
    from app.db.database import Base
    Base.metadata.drop_all(conn)


@pytest.fixture(scope="function")
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client():
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
    os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("FRONTEND_DIST", "")

    from main import app

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    from app.db.database import get_db
    app.dependency_overrides[get_db] = override_get_db

    app.middleware_stack = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def demo_user_payload():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Test1234",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
async def auth_token(client, demo_user_payload):
    from app.api.auth import hash_password
    from app.models.models import User

    async with TestSessionLocal() as session:
        user = User(
            username=demo_user_payload["username"],
            email=demo_user_payload["email"],
            hashed_password=hash_password(demo_user_payload["password"]),
            first_name=demo_user_payload["first_name"],
            last_name=demo_user_payload["last_name"],
            is_verified=True,
            is_active=True,
            rating=1000,
        )
        session.add(user)
        await session.commit()

    r = await client.post("/api/auth/login", json={
        "login": demo_user_payload["username"],
        "password": demo_user_payload["password"],
    })
    assert r.status_code == 200, f"login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
