"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.server import router as oauth_router
from app.rate_limit import limiter
from app.routers.molecular_sequence import router as molecular_sequence_router
from app.routers.system import router as system_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="fhir-api",
        description=(
            "Async FHIR R4 MolecularSequence REST API (Phase 2 GenomeRSE portfolio service). "
            "See README.md: the OAuth2 layer is a self-contained demo Authorization Server."
        ),
        version="0.1.0",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(oauth_router)
    app.include_router(molecular_sequence_router)
    app.include_router(system_router)
    return app


app = create_app()
