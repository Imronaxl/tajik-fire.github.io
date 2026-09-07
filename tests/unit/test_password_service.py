"""Unit-тесты для PasswordService."""
import pytest

from app.services.password_service import PasswordService


class TestPasswordValidation:
    def test_valid_password(self):
        ok, msg = PasswordService.validate_password("Test1234")
        assert ok is True
        assert msg == ""

    def test_too_short(self):
        ok, msg = PasswordService.validate_password("Test1")
        assert ok is False
        assert "at least" in msg

    def test_no_uppercase(self):
        ok, msg = PasswordService.validate_password("test1234")
        assert ok is False
        assert "uppercase" in msg

    def test_no_lowercase(self):
        ok, msg = PasswordService.validate_password("TEST1234")
        assert ok is False
        assert "lowercase" in msg

    def test_no_digit(self):
        ok, msg = PasswordService.validate_password("TestTest")
        assert ok is False
        assert "digit" in msg

    def test_empty(self):
        ok, msg = PasswordService.validate_password("")
        assert ok is False

    def test_requirements_dict(self):
        req = PasswordService.get_password_requirements()
        assert req["min_length"] == 8
        assert req["requires_uppercase"] is True
        assert req["requires_lowercase"] is True
        assert req["requires_digit"] is True
