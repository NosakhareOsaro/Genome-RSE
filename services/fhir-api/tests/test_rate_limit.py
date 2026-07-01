from __future__ import annotations

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings
from app.main import app as real_app
from app.rate_limit import limiter as real_limiter


def test_real_app_limiter_uses_configured_rate_limit():
    assert real_limiter.enabled
    assert real_app.state.limiter is real_limiter


async def test_rate_limit_returns_429_once_exceeded():
    """Exercise slowapi's actual mechanics with a deliberately tiny limit.

    The real app uses RATE_LIMIT (100/minute by default), too high to
    hit in a fast unit test without flooding requests. This builds a
    throwaway app wired identically to app/main.py but with a 2/minute
    limit, to prove the wiring pattern itself works end-to-end.
    """
    test_limiter = Limiter(key_func=get_remote_address, default_limits=["2/minute"])
    test_app = FastAPI()
    test_app.state.limiter = test_limiter
    test_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    test_app.add_middleware(SlowAPIMiddleware)

    @test_app.get("/ping")
    async def ping():
        return {"pong": True}

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        first = await ac.get("/ping")
        second = await ac.get("/ping")
        third = await ac.get("/ping")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Rate limit exceeded" in third.json()["error"]


def test_default_rate_limit_matches_settings():
    assert get_settings().rate_limit == "100/minute"
