"""Unit-тесты для судьи (Verifiers)."""
import pytest

from app.services.judger.verifiers import Verifier


class TestVerifier:
    def test_exact_match(self):
        ok, err = Verifier.compare_outputs("hello\n", "hello\n")
        assert ok is True

    def test_trailing_whitespace_ignored(self):
        ok, err = Verifier.compare_outputs("hello\n", "hello   \n")
        assert ok is True

    def test_different_lines(self):
        ok, err = Verifier.compare_outputs("hello\nworld\n", "hello\nworld\nextra\n")
        assert ok is False
        assert "too long" in err.lower() or "too short" in err.lower()

    def test_wrong_at_line(self):
        ok, err = Verifier.compare_outputs("hello\nworld\n", "hello\nworld2\n")
        assert ok is False
        assert "line 2" in err

    def test_empty_outputs(self):
        ok, err = Verifier.compare_outputs("", "")
        assert ok is True

    def test_case_sensitive(self):
        ok, err = Verifier.compare_outputs("Hello", "hello")
        assert ok is False

    def test_case_insensitive(self):
        ok, err = Verifier.compare_outputs("Hello", "hello", ignore_case=True)
        assert ok is True
