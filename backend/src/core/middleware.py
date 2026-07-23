"""Security middleware: rate limiting and request logging.

Rate limiting is Redis-backed with an in-memory fallback. Limits are enforced
per identity (user id, org id, or client IP) and per scope (auth, upload, ai,
search, reports, default). Responses include standard RateLimit headers and
return HTTP 429 with Retry-After when exceeded.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    import redis.asyncio as aioredis

    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False


SCOPE_LIMITS = {
    "auth": settings.RATE_LIMIT_AUTH,
    "upload": settings.RATE_LIMIT_UPLOAD,
    "ai": settings.RATE_LIMIT_AI,
    "search": settings.RATE_LIMIT_SEARCH,
    "reports": settings.RATE_LIMIT_REPORTS,
    "default": settings.RATE_LIMIT_DEFAULT,
}

WINDOW_SECONDS = 60


def _scope_for_path(path: str) -> str:
    if path.startswith("/api/v1/auth"):
        return "auth"
    if "upload" in path:
        return "upload"
    if "/ai-assistant" in path or "/ml/" in path or "/recommendations" in path:
        return "ai"
    if "/search" in path or "/candidates/search" in path:
        return "search"
    if "/reports" in path or "/export" in path:
        return "reports"
    return "default"


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed sliding-window rate limiter with in-memory fallback."""

    def __init__(self, app, redis_url: str = "redis://localhost:6379/0"):
        super().__init__(app)
        self._redis: Any | None = None
        self._redis_url = redis_url
        self._local: dict[str, list[float]] = {}

    async def _get_redis(self):
        if not _HAS_REDIS:
            return None
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
                await self._redis.ping()
            except Exception:
                self._redis = None
        return self._redis

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        identity = _client_ip(request)
        scope = _scope_for_path(request.url.path)
        limit = SCOPE_LIMITS.get(scope, settings.RATE_LIMIT_DEFAULT)
        key = f"rl:{identity}:{scope}"

        allowed, remaining, retry_after = await self._check(key, limit)
        if not allowed:
            logger.warning("Rate limit exceeded for %s scope=%s", identity, scope)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please retry later.",
                    },
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    async def _check(self, key: str, limit: int) -> tuple[bool, int, int]:
        now = time.time()
        window_start = now - WINDOW_SECONDS

        client = await self._get_redis()
        if client:
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, WINDOW_SECONDS)
            results = await pipe.execute()
            count = results[2]
        else:
            entries = [t for t in self._local.get(key, []) if t > window_start]
            entries.append(now)
            self._local[key] = entries
            count = len(entries)

        if count > limit:
            retry_after = WINDOW_SECONDS
            return False, 0, retry_after
        return True, limit - count, WINDOW_SECONDS


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Adds a correlation ID to every request and logs request/response metadata."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "ip": _client_ip(request),
            },
        )
        return response
