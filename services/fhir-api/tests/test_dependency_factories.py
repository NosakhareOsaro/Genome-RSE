"""Covers the production get_db_session/get_redis factories themselves.

Every other test overrides these dependencies with test doubles (see
conftest.py) -- that's deliberate, but it means the real factory bodies
need their own direct exercise. Both are safe to call without a live
Postgres/Redis: SQLAlchemy's AsyncSession and redis-py's async client
don't actually connect until a query/command is issued.
"""

from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.db import get_db_session


def test_get_redis_returns_a_client_without_connecting():
    client = get_redis()
    assert isinstance(client, Redis)
    # Calling again returns the same cached client instance.
    assert get_redis() is client


async def test_get_db_session_yields_a_session_without_connecting():
    async for session in get_db_session():
        assert isinstance(session, AsyncSession)
        break
