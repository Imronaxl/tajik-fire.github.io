"""E2E тесты через Playwright.

Запуск:
    cd fastapi_app && uvicorn main:app --reload &
    pytest tests/e2e/ -v
"""
import asyncio
import os

import pytest

playwright = pytest.importorskip("playwright")
from playwright.async_api import async_playwright


BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()


@pytest.mark.asyncio
class TestUserJourney:
    async def test_homepage_loads(self, browser):
        page = await browser.new_page()
        await page.goto(BASE_URL)
        await page.wait_for_selector("nav.navbar", timeout=10000)
        title = await page.title()
        assert title == "tajik-fire"
        await page.close()

    async def test_login_page_renders(self, browser):
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/login")
        await page.wait_for_selector("input#login-username", timeout=10000)
        await page.close()

    async def test_problems_page_renders(self, browser):
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/problems")
        await page.wait_for_selector("div.page", timeout=10000)
        await page.close()

    async def test_leaderboard_page_renders(self, browser):
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/leaderboard")
        await page.wait_for_selector("div.page", timeout=10000)
        await page.close()

    async def test_language_switcher_present(self, browser):
        page = await browser.new_page()
        await page.goto(BASE_URL)
        await page.wait_for_selector(".lang-switcher", timeout=10000)
        await page.close()

    async def test_ai_assistant_button_present(self, browser):
        page = await browser.new_page()
        await page.goto(BASE_URL)
        await page.wait_for_selector(".ai-fab", timeout=10000)
        await page.close()

    async def test_404_page(self, browser):
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/nonexistent-page-12345")
        await page.wait_for_timeout(1000)
        content = await page.content()
        assert "404" in content or "ёфт нашуд" in content or "не найден" in content
        await page.close()

    async def test_login_with_demo_account(self, browser):
        page = await browser.new_page()
        await page.goto(f"{BASE_URL}/login")
        await page.wait_for_selector("#login-username", state="visible", timeout=10000)
        await page.fill("#login-username", "demo")
        await page.fill("#login-password", "Demo1234")
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(2000)
        await page.close()
