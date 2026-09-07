import asyncio
import os
import subprocess
import time
import signal
from playwright.async_api import async_playwright

ROOT = "/home/z/my-project/repo"
SCREENSHOT_DIR = f"{ROOT}/docs/screenshots"
BASE_URL = "http://127.0.0.1:8777"

SHOTS = [
    ("/", "01-home.png", 1440, 900, False),
    ("/login", "02-auth.png", 1440, 900, False),
    ("/problems", "03-problems.png", 1440, 900, True),
    ("/problems/1", "04-problem-detail.png", 1440, 900, True),
    ("/problems/1/solve", "05-editor.png", 1440, 900, True),
    ("/leaderboard", "08-leaderboard.png", 1440, 900, True),
    ("/submissions", "09-submissions.png", 1440, 900, True),
    ("/learning", "10-learning.png", 1440, 900, True),
    ("/learning/intro-to-algorithms", "11-learning-detail.png", 1440, 900, True),
    ("/tasks", "12-tasks.png", 1440, 900, True),
    ("/messenger", "13-messenger.png", 1440, 900, True),
    ("/profile", "14-profile.png", 1440, 900, True),
    ("/news", "15-news.png", 1440, 900, True),
    ("/olympiads", "16-contests.png", 1440, 900, True),
    ("/docs", "17-swagger-docs.png", 1440, 900, False),
    ("/", "18-mobile-home.png", 390, 844, False),
]


async def login(page):
    await page.wait_for_selector("#login-username", state="visible", timeout=10000)
    await page.fill("#login-username", "demo")
    await page.fill("#login-password", "Demo1234")
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(1200)


async def seed_submission(page):
    await page.goto(f"{BASE_URL}/problems/1/solve")
    await page.wait_for_timeout(500)
    await page.select_option(".lang-select", "python3")
    await page.fill(".code", "a, b = map(int, input().split())\nprint(a + b)")
    await page.click("button:has-text('Отправить')")
    await page.wait_for_timeout(3000)


async def main():
    env = dict(os.environ)
    env.update({
        "DEBUG": "True",
        "SECRET_KEY": "screenshot-secret-key-not-for-prod",
        "DATABASE_URL": "sqlite+aiosqlite:///./devstudio.db",
        "FRONTEND_DIST": f"{ROOT}/frontend/dist",
        "PYTHONPATH": f"{ROOT}/fastapi_app",
    })
    os.chdir(f"{ROOT}/fastapi_app")
    if os.path.exists("devstudio.db"):
        os.remove("devstudio.db")

    proc = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8777"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    try:
        import urllib.request
        for _ in range(40):
            try:
                urllib.request.urlopen(f"{BASE_URL}/health", timeout=0.5)
                break
            except Exception:
                time.sleep(0.25)
        else:
            out = proc.stdout.read(4000).decode("utf-8", errors="ignore")
            print("server didn't start")
            print(out)
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            page = await ctx.new_page()
            await page.goto(f"{BASE_URL}/login")
            await login(page)
            await seed_submission(page)
            await ctx.close()

            os.makedirs(SCREENSHOT_DIR, exist_ok=True)

            for path, name, w, h, authed in SHOTS:
                ctx = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2)
                page = await ctx.new_page()
                if authed:
                    await page.goto(f"{BASE_URL}/login")
                    await login(page)
                await page.goto(f"{BASE_URL}{path}")
                await page.wait_for_timeout(1500)
                target = f"{SCREENSHOT_DIR}/{name}"
                await page.screenshot(path=target, full_page=False)
                print(f"  saved {name} ({w}x{h})")
                await ctx.close()

            await browser.close()
            print("done")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


asyncio.run(main())
