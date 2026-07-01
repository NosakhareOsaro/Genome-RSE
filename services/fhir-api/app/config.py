"""Application settings, loaded from environment variables (see .env.example)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://fhir:fhir@localhost:5432/fhir"

    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 60

    # Demo OAuth2 Authorization Server. NOT connected to a real EHR/IdP --
    # see app/auth/server.py and the service README for details. These
    # defaults are obvious non-secrets, matching .env.example.
    demo_client_id: str = "demo-client"
    demo_client_secret: str = "REPLACE_ME_NOT_A_REAL_SECRET"
    jwt_signing_key: str = "REPLACE_ME_NOT_A_REAL_SECRET"
    jwt_expires_in_seconds: int = 3600

    rate_limit: str = "100/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()
