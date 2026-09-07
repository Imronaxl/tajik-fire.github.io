from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.auth import get_current_user_optional
from app.models.models import User
from app.modules.ai_assistant.schemas import ChatRequest, ChatResponse
from app.modules.ai_assistant.service import generate_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    return generate_reply(request)


@router.get("/status")
async def status():
    return {
        "available": False,
        "provider": "placeholder",
        "features": ["hint", "explain", "review", "translate"],
        "languages": ["tg", "ru", "en"],
    }
