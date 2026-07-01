"""Demo OAuth2 Authorization Server (client_credentials grant only).

################################################################################
# THIS IS A SELF-CONTAINED DEMO AUTHORIZATION SERVER.
# It is NOT connected to any real EHR, identity provider, or SMART on FHIR
# launch sequence. It exists to demonstrate OAuth2-protected FHIR endpoints
# for a portfolio project. Do not treat it as production identity
# infrastructure, and never point it at real patient data with the default
# placeholder secrets. See the top-level service README for details.
################################################################################

Token issuance (`POST /oauth/token`) is a small custom implementation of
RFC 6749's client_credentials grant -- Authlib does not ship an official
FastAPI/Starlette Authorization Server integration (only Flask/Django),
so this module builds request validation directly on top of Authlib's
``authlib.oauth2.rfc6749.errors`` for spec-conformant error responses,
and mints tokens with ``joserfc`` (Authlib's own recommended successor
to its deprecated ``authlib.jose`` module). Resource-side token
*validation* (see ``app/auth/security.py``) does use Authlib's official
``ResourceProtector``/``TokenValidator`` framework.
"""

from __future__ import annotations

import hmac
import time
from typing import Any

from authlib.oauth2.rfc6749.errors import (
    InvalidClientError,
    InvalidScopeError,
    OAuth2Error,
    UnsupportedGrantTypeError,
)
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from joserfc import jwt
from joserfc.jwk import OctKey

from app.config import get_settings

ALLOWED_SCOPES = {"system/MolecularSequence.read", "system/MolecularSequence.write"}
DEFAULT_SCOPES = {"system/MolecularSequence.read"}
ISSUER = "fhir-api-demo"
AUDIENCE = "fhir-api"

router = APIRouter(tags=["auth"])


def get_signing_key() -> OctKey:
    return OctKey.import_key(get_settings().jwt_signing_key)


def issue_token(
    *, grant_type: str, client_id: str, client_secret: str, scope: str | None
) -> dict[str, Any]:
    """Validate a client_credentials token request and mint a JWT.

    Raises an ``authlib.oauth2.rfc6749.errors.OAuth2Error`` subclass on
    any validation failure, matching RFC 6749 error semantics.
    """
    settings = get_settings()

    if grant_type != "client_credentials":
        raise UnsupportedGrantTypeError(grant_type)

    client_id_ok = hmac.compare_digest(client_id, settings.demo_client_id)
    client_secret_ok = hmac.compare_digest(client_secret, settings.demo_client_secret)
    if not (client_id_ok and client_secret_ok):
        raise InvalidClientError()

    requested_scopes = set(scope.split()) if scope else set(DEFAULT_SCOPES)
    if not requested_scopes <= ALLOWED_SCOPES:
        raise InvalidScopeError()

    now = int(time.time())
    expires_in = settings.jwt_expires_in_seconds
    granted_scope = " ".join(sorted(requested_scopes))
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": client_id,
        "scope": granted_scope,
        "iat": now,
        "exp": now + expires_in,
    }
    token = jwt.encode({"alg": "HS256"}, claims, get_signing_key())

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "scope": granted_scope,
    }


@router.post("/oauth/token")
async def token_endpoint(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str | None = Form(default=None),
) -> JSONResponse:
    try:
        token_response = issue_token(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
        )
    except OAuth2Error as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error, "error_description": exc.description},
        )
    return JSONResponse(content=token_response)
