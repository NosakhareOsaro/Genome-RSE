"""Cache-aside Redis helpers for MolecularSequence reads.

Pattern: reads check the cache first and populate it on a miss; writes
(update/delete) explicitly invalidate the entry rather than waiting for
TTL expiry, so a read immediately after a write never serves stale data.

`get_redis` is a FastAPI dependency; tests override it with a shared
`fakeredis` instance (see tests/conftest.py) instead of connecting to a
real Redis server.
"""

from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.config import get_settings

_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(get_settings().redis_url, decode_responses=True)
    return _redis_client


def _cache_key(resource_id: str) -> str:
    return f"molseq:{resource_id}"


async def get_cached_resource(redis: Redis, resource_id: str) -> dict[str, Any] | None:
    raw = await redis.get(_cache_key(resource_id))
    if raw is None:
        return None
    return json.loads(raw)


async def set_cached_resource(
    redis: Redis, resource_id: str, resource: dict[str, Any], ttl_seconds: int
) -> None:
    await redis.set(_cache_key(resource_id), json.dumps(resource), ex=ttl_seconds)


async def invalidate_cached_resource(redis: Redis, resource_id: str) -> None:
    await redis.delete(_cache_key(resource_id))
