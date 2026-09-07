import re

from app.core.config import settings


class PasswordService:

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        if not password:
            return False, "password is required"
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False, f"password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"
        if not re.search(r"[A-Z]", password):
            return False, "password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "password must contain at least one digit"
        return True, ""

    @staticmethod
    def get_password_requirements() -> dict:
        return {
            "min_length": settings.PASSWORD_MIN_LENGTH,
            "requires_uppercase": True,
            "requires_lowercase": True,
            "requires_digit": True,
        }
