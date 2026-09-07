"""Unit-тесты для EmailService."""
import pytest

from app.services.email_service import EmailService


class TestEmailService:
    def test_generate_code_is_six_digits(self):
        for _ in range(20):
            code = EmailService.generate_code()
            assert len(code) == 6
            assert code.isdigit()

    def test_generate_code_is_random(self):
        codes = {EmailService.generate_code() for _ in range(50)}
        assert len(codes) > 40

    def test_verification_email_html_contains_code(self):
        html = EmailService.verification_email_html("123456", 30)
        assert "123456" in html
        assert "30" in html

    def test_reset_password_email_html_contains_code(self):
        html = EmailService.reset_password_email_html("654321", 15)
        assert "654321" in html
        assert "15" in html

    @pytest.mark.asyncio
    async def test_send_email_returns_false_without_smtp(self):
        result = await EmailService.send_email("test@example.com", "test", "<p>hi</p>")
        assert result is False
