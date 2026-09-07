import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, storage=None):
        super().__init__(app)
        self.storage: Dict[str, Dict[str, list]] = storage if storage is not None else defaultdict(lambda: defaultdict(list))
        self.limits = {
            "POST /api/auth/login": {"limit": 10, "window": 60},
            "POST /api/auth/register": {"limit": 5, "window": 3600},
            "POST /api/auth/reset-password-request": {"limit": 5, "window": 3600},
            "POST /api/problems/submissions": {"limit": 20, "window": 60},
            "POST /api/messenger/messages": {"limit": 30, "window": 60},
            "POST /api/news": {"limit": 10, "window": 60},
        }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/static") or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        endpoint_key = f"{request.method} {path}"
        config = self.limits.get(endpoint_key)
        if config is None:
            return await call_next(request)

        user_id = self._identify_client(request)
        now = time.time()
        window = config["window"]
        limit = config["limit"]

        bucket = self.storage[user_id][endpoint_key]
        bucket[:] = [ts for ts in bucket if now - ts < window]

        if len(bucket) >= limit:
            retry_after = max(1, int(window - (now - bucket[0])))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": f"rate limit exceeded, retry in {retry_after}s"},
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)
        return await call_next(request)

    @staticmethod
    def _identify_client(request: Request) -> str:
        user = getattr(request.state, "user", None)
        if user is not None and hasattr(user, "id"):
            return f"user:{user.id}"
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
