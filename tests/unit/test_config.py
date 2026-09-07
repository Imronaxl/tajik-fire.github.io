"""Unit-тесты для конфигурации."""
import os

from app.core.config import Settings


class TestConfig:
    def test_default_values(self, monkeypatch):
        monkeypatch.delenv("SECRET_KEY", raising=False)
        s = Settings()
        assert s.PROJECT_NAME == "tajik-fire"
        assert s.DEBUG is True
        assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert s.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert s.PASSWORD_MIN_LENGTH == 8

    def test_email_disabled_by_default(self):
        s = Settings()
        assert s.email_enabled is False

    def test_email_enabled_with_smtp(self, monkeypatch):
        monkeypatch.setenv("SMTP_USER", "user@example.com")
        monkeypatch.setenv("SMTP_PASSWORD", "pass")
        s = Settings()
        assert s.email_enabled is True

    def test_allowed_origins_default(self):
        s = Settings()
        assert "http://localhost:8000" in s.ALLOWED_ORIGINS
