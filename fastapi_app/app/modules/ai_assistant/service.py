from typing import List

from app.modules.ai_assistant.schemas import ChatMessage, ChatRequest, ChatResponse, SYSTEM_PROMPTS


PLACEHOLDER_REPLIES_TG = [
    "ИИ-ёрдамчи ҳанӯз дар ҳоли тайёрӣ аст. Дар наздиктар рӯй на медиҳем!",
    "Бубахшед, ман ҳоло ҷавоб дода наметавонам. Лутфан баъдтар кӯшиш кунед.",
    "Дархости шумо сабт шуд. Вақте ки ИИ фаъол шавад, мо ба шумо хабар медиҳем.",
]

PLACEHOLDER_REPLIES_RU = [
    "ИИ-ассистент пока находится в разработке. Скоро запустим!",
    "Извините, я пока не могу ответить. Попробуйте позже.",
    "Ваш запрос записан. Когда ИИ заработает, мы сообщим.",
]

PLACEHOLDER_REPLIES_EN = [
    "The AI assistant is still in development. Coming soon!",
    "Sorry, I cannot answer yet. Please try again later.",
    "Your request has been recorded. We will notify you when AI is live.",
]


def generate_reply(request: ChatRequest) -> ChatResponse:
    lang = request.language if request.language in ("tg", "ru", "en") else "tg"
    if lang == "ru":
        replies = PLACEHOLDER_REPLIES_RU
    elif lang == "en":
        replies = PLACEHOLDER_REPLIES_EN
    else:
        replies = PLACEHOLDER_REPLIES_TG

    idx = hash(request.message) % len(replies)
    if idx < 0:
        idx = -idx

    return ChatResponse(
        reply=replies[idx],
        sources=[],
        suggested_actions=["/problems", "/learning", "/leaderboard"],
        provider="placeholder",
        latency_ms=0,
    )


def get_system_prompt(language: str) -> str:
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["tg"])
