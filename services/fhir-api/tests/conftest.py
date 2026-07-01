from __future__ import annotations

from collections.abc import AsyncIterator

import fakeredis.aioredis as fakeredis
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.cache import get_redis
from app.db import get_db_session
from app.main import app
from app.models.orm import Base

DEMO_CLIENT_ID = "demo-client"
DEMO_CLIENT_SECRET = "REPLACE_ME_NOT_A_REAL_SECRET"


@pytest_asyncio.fixture
async def db_session_factory():
    """A fresh in-memory SQLite DB per test, shared across connections via StaticPool."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield session_factory
    await engine.dispose()


@pytest_asyncio.fixture
async def fake_redis():
    fake = fakeredis.FakeRedis(decode_responses=True)
    yield fake
    await fake.aclose()


@pytest_asyncio.fixture
async def client(db_session_factory, fake_redis) -> AsyncIterator[AsyncClient]:
    async def override_get_db_session() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as session:
            yield session

    def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _issue_token(client: AsyncClient, scope: str) -> str:
    response = await client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": DEMO_CLIENT_ID,
            "client_secret": DEMO_CLIENT_SECRET,
            "scope": scope,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def read_write_headers(client: AsyncClient) -> dict[str, str]:
    token = await _issue_token(
        client, "system/MolecularSequence.read system/MolecularSequence.write"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def read_only_headers(client: AsyncClient) -> dict[str, str]:
    token = await _issue_token(client, "system/MolecularSequence.read")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def write_only_headers(client: AsyncClient) -> dict[str, str]:
    token = await _issue_token(client, "system/MolecularSequence.write")
    return {"Authorization": f"Bearer {token}"}
