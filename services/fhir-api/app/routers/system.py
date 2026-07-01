"""System-level endpoints: FHIR CapabilityStatement and a health check.

Both are unauthenticated, matching common FHIR server / ops convention
(a client needs to read the CapabilityStatement *before* it knows how
to authenticate, and health checks are consumed by infrastructure, not
API clients).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.server import ALLOWED_SCOPES
from app.db import get_db_session

router = APIRouter(tags=["system"])

FHIR_VERSION = "4.0.1"


@router.get("/metadata")
async def capability_statement() -> dict[str, Any]:
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": date.today().isoformat(),
        "kind": "instance",
        "software": {"name": "fhir-api", "version": "0.1.0"},
        "fhirVersion": FHIR_VERSION,
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "security": {
                    "service": [
                        {
                            "coding": [
                                {
                                    "system": (
                                        "http://terminology.hl7.org/"
                                        "CodeSystem/restful-security-service"
                                    ),
                                    "code": "SMART-on-FHIR",
                                }
                            ]
                        }
                    ],
                    "extension": [
                        {
                            "url": "http://fhir-api.example/StructureDefinition/demo-auth-server-notice",
                            "valueString": (
                                "This server's OAuth2 layer is a self-contained demo "
                                "Authorization Server, not a real EHR/IdP."
                            ),
                        }
                    ],
                },
                "resource": [
                    {
                        "type": "MolecularSequence",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                            {"code": "create"},
                            {"code": "update"},
                            {"code": "delete"},
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "_count", "type": "number"},
                        ],
                    }
                ],
            }
        ],
        "extension": [{"url": "allowed-scopes", "valueString": " ".join(sorted(ALLOWED_SCOPES))}],
    }


@router.get("/healthz")
async def healthz(session: Annotated[AsyncSession, Depends(get_db_session)]) -> dict[str, Any]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "time": datetime.now(UTC).isoformat()}
