"""Async SQLAlchemy engine/session setup.

`get_db_session` is a FastAPI dependency; tests override it entirely
(see tests/conftest.py) to point at an in-memory SQLite database instead
of the real Postgres configured via DATABASE_URL, so importing this
module never requires a reachable database -- `create_async_engine`
doesn't connect until a session is actually used.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

_settings = get_settings()

engine = create_async_engine(_settings.database_url, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
