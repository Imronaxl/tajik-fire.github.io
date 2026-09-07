import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.db.database import init_db
from app.api import (
    auth, users, messenger, tasks, olympiads,
    problems, news, learning, admin, friends, stats,
)
from app.middleware.rate_limiter import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s | %(name)-12s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("devstudio")


def _gettext(value: str) -> str:
    return value


templates = Jinja2Templates(directory="app/templates")
templates.env.globals["_"] = _gettext
templates.env.globals["project_name"] = settings.PROJECT_NAME
templates.env.globals["project_version"] = settings.VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("app started v%s", settings.VERSION)
    yield
    logger.info("app shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Competitive programming platform with judger, learning tracks and social features.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

api_prefix = "/api"
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Users"])
app.include_router(messenger.router, prefix=f"{api_prefix}/messenger", tags=["Messenger"])
app.include_router(tasks.router, prefix=f"{api_prefix}/tasks", tags=["Tasks"])
app.include_router(problems.router, prefix=f"{api_prefix}/problems", tags=["Problems"])
app.include_router(olympiads.router, prefix=f"{api_prefix}/olympiads", tags=["Olympiads"])
app.include_router(news.router, prefix=f"{api_prefix}", tags=["News"])
app.include_router(learning.router, prefix=f"{api_prefix}/learning", tags=["Learning"])
app.include_router(friends.router, prefix=f"{api_prefix}/friends", tags=["Friends"])
app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["Admin"])
app.include_router(stats.router, prefix=f"{api_prefix}", tags=["Stats"])


PAGES = {
    "/": "index.html",
    "/auth": "auth.html",
    "/login": "auth.html",
    "/register": "auth.html",
    "/problems": "problems.html",
    "/olympiads": "olympiads.html",
    "/contests": "olympiads.html",
    "/tasks": "tasks.html",
    "/messenger": "messenger.html",
    "/learning": "learning.html",
    "/news": "news.html",
    "/profile": "profile.html",
    "/leaderboard": "leaderboard.html",
    "/submissions": "submissions.html",
    "/editor": "editor.html",
}

DYNAMIC_PAGES = [
    ("/problems/{problem_id}/solve", "editor.html"),
    ("/learning/{slug}", "learning.html"),
]


def _render_page(request: Request, template_name: str):
    return templates.TemplateResponse(template_name, {
        "request": request,
        "current_user": None,
    })


for route, template in PAGES.items():
    def _make_handler(tpl=template):
        async def _handler(request: Request):
            return _render_page(request, tpl)
        return _handler
    app.add_api_route(route, _make_handler(), methods=["GET"], include_in_schema=False)


for route, template in DYNAMIC_PAGES:
    def _make_dynamic_handler(tpl=template):
        async def _handler(request: Request):
            return _render_page(request, tpl)
        return _handler
    app.add_api_route(route, _make_dynamic_handler(), methods=["GET"], include_in_schema=False)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION, "debug": settings.DEBUG}


@app.get("/api", tags=["Meta"])
async def api_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }
