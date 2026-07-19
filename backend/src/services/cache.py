"""Redis caching layer with invalidation support.

Wraps a Redis client (or an in-memory fallback when Redis is unavailable) and
provides namespaced get/set/delete helpers for rankings, jobs, summaries,
search results, and analytics.

Cache keys follow the pattern: ats:{namespace}:{id}[:params]
Invalidation is namespace-aware: deleting by namespace clears all keys in it.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False


class CacheService:
    """Async cache service backed by Redis with an in-memory fallback."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis: Optional[Any] = None
        self._fallback: dict[str, str] = {}
        self._redis_url = redis_url

    async def _get_redis(self) -> Optional[Any]:
        if not _HAS_REDIS:
            return None
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
                await self._redis.ping()
            except Exception as exc:
                logger.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
                self._redis = None
        return self._redis

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        full_key = self._full_key(namespace, key)
        client = await self._get_redis()
        if client:
            raw = await client.get(full_key)
        else:
            raw = self._fallback.get(full_key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        full_key = self._full_key(namespace, key)
        raw = json.dumps(value, default=str)
        client = await self._get_redis()
        if client:
            await client.set(full_key, raw, ex=ttl)
        else:
            self._fallback[full_key] = raw

    async def delete(self, namespace: str, key: str) -> None:
        full_key = self._full_key(namespace, key)
        client = await self._get_redis()
        if client:
            await client.delete(full_key)
        else:
            self._fallback.pop(full_key, None)

    async def invalidate_namespace(self, namespace: str) -> None:
        """Delete all keys in a namespace."""
        client = await self._get_redis()
        if client:
            pattern = f"ats:{namespace}:*"
            async for key in client.scan_iter(match=pattern):
                await client.delete(key)
        else:
            prefix = f"ats:{namespace}:"
            self._fallback = {k: v for k, v in self._fallback.items() if not k.startswith(prefix)}

    @staticmethod
    def _full_key(namespace: str, key: str) -> str:
        return f"ats:{namespace}:{key}"


cache_service = CacheService()
