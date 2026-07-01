"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from app.auth.server import router as oauth_router
from app.routers.molecular_sequence import router as molecular_sequence_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="fhir-api",
        description=(
            "Async FHIR R4 MolecularSequence REST API (Phase 2 GenomeRSE portfolio service). "
            "See README.md: the OAuth2 layer is a self-contained demo Authorization Server."
        ),
        version="0.1.0",
    )
    app.include_router(oauth_router)
    app.include_router(molecular_sequence_router)
    return app


app = create_app()
