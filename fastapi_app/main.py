import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

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
logger = logging.getLogger("tajik_fire")

FRONTEND_DIST = os.environ.get("FRONTEND_DIST", os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
FRONTEND_EXISTS = os.path.isdir(FRONTEND_DIST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("tajik-fire v%s started", settings.VERSION)
    if FRONTEND_EXISTS:
        logger.info("serving frontend from %s", FRONTEND_DIST)
    else:
        logger.warning("frontend dist not built; run `npm run build` in frontend/")
    yield
    logger.info("tajik-fire shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Платформа соревновательного программирования с песочницей-судьёй, учебными треками и социальной лентой.",
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

from app.modules import ai_assistant as ai_module
ai_module.register()
from app.modules.registry import list_modules, get_all_routers
for router_instance, prefix, tags in get_all_routers():
    app.include_router(router_instance, prefix=prefix, tags=tags)
logger.info("registered modules: %s", [m.name for m in list_modules()])

if FRONTEND_EXISTS:
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    favicon = os.path.join(FRONTEND_DIST, "favicon.svg")
    if os.path.exists(favicon):
        app.mount("/favicon.svg", StaticFiles(directory=FRONTEND_DIST), name="favicon")


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


INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html") if FRONTEND_EXISTS else None


@app.get("/{path:path}", include_in_schema=False)
async def spa_fallback(request: Request, path: str):
    if path.startswith("api/") or path.startswith("docs") or path.startswith("redoc") or path.startswith("health"):
        return {"detail": "not found"}

    if path.startswith("assets/"):
        full = os.path.join(FRONTEND_DIST, path)
        if os.path.isfile(full):
            return FileResponse(full)
        return {"detail": "asset not found"}

    candidate = os.path.join(FRONTEND_DIST, path)
    if path and os.path.isfile(candidate):
        return FileResponse(candidate)

    if INDEX_HTML and os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)

    return HTMLResponse(
        "<h1>tajik-fire backend is up</h1>"
        "<p>Frontend not built. Run <code>npm install &amp;&amp; npm run build</code> in <code>frontend/</code>.</p>",
        status_code=200,
    )
