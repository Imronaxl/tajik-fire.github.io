import os
import secrets
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "tajik-fire"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./devstudio.db"

    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]

    PASSWORD_MIN_LENGTH: int = 8

    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.yandex.ru")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@devstudio.local")

    EMAIL_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 60

    JUDGER_BACKEND: str = os.getenv("JUDGER_BACKEND", "subprocess")
    JUDGER_WORKDIR: str = os.getenv("JUDGER_WORKDIR", "/tmp/devstudio-judge")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD)


settings = Settings()
