from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.models import News, User
from app.schemas.schemas import NewsCreate, NewsResponse

router = APIRouter()


@router.get("/news", response_model=List[NewsResponse])
async def list_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(News)
        .where(News.is_published.is_(True))
        .options(selectinload(News.author))
        .order_by(desc(News.published_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [_news_to_response(n) for n in items]


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(News).options(selectinload(News.author)).where(News.id == news_id)
    )
    news = result.scalar_one_or_none()
    if news is None or not news.is_published:
        raise HTTPException(status_code=404, detail="news not found")
    return _news_to_response(news)


@router.post("/news", response_model=NewsResponse, status_code=201)
async def create_news(
    payload: NewsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    news = News(
        title=payload.title,
        content=payload.content,
        author_id=current_user.id,
        is_published=True,
        published_at=datetime.now(timezone.utc),
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    news.author = current_user
    return _news_to_response(news)


@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    payload: NewsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(News).options(selectinload(News.author)).where(News.id == news_id)
    )
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="news not found")
    if news.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized")

    news.title = payload.title
    news.content = payload.content
    news.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(news)
    return _news_to_response(news)


@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if news is None:
        raise HTTPException(status_code=404, detail="news not found")
    if news.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="not authorized")
    await db.delete(news)
    await db.commit()
    return {"message": "news deleted"}


def _news_to_response(news: News) -> NewsResponse:
    return NewsResponse(
        id=news.id,
        title=news.title,
        content=news.content,
        author_id=news.author_id,
        author_username=news.author.username if news.author else None,
        is_published=news.is_published,
        published_at=news.published_at,
        created_at=news.created_at,
        updated_at=news.updated_at,
    )
