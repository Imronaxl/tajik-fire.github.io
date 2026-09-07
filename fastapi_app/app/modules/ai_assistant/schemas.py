from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    context: Optional[List[ChatMessage]] = []
    language: str = "tg"


class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = []
    suggested_actions: List[str] = []
    provider: str = "placeholder"
    latency_ms: int = 0


SYSTEM_PROMPTS = {
    "tg": (
        "Шумо ёрдамчи ИИ-и платформаи tajik-fire ҳастед. "
        "Ба корбарон кумак кунед: дар ҳали масъалаҳо, фаҳмиши шароит, "
        "нашри навсозиҳо ва ғайра. Забон: тоҷикӣ."
    ),
    "ru": (
        "Ты ИИ-ассистент платформы tajik-fire. "
        "Помогай пользователям в решении задач, понимании условий, "
        "объяснении вердиктов и обучении. Язык: русский."
    ),
    "en": (
        "You are an AI assistant for the tajik-fire platform. "
        "Help users solve problems, understand statements, explain verdicts, "
        "and learn. Language: English."
    ),
}
