from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()


from app.models import *  # noqa: E402,F401,F403


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.data.seed_problems import seed_demo_data

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.models.models import Problem

        existing = await session.execute(select(Problem).limit(1))
        if existing.scalar_one_or_none() is None:
            try:
                await seed_demo_data(session)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("seeding skipped: %s", exc)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
