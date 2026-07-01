"""Resource-server side OAuth2 bearer token validation.

Unlike token *issuance* (app/auth/server.py, a custom implementation),
this module uses Authlib's official resource-protection framework
(``ResourceProtector`` / ``TokenValidator``) to enforce bearer auth and
SMART-style scopes on FHIR endpoints.
"""

from __future__ import annotations

import time
from typing import Any

from authlib.oauth2.rfc6749.errors import OAuth2Error
from authlib.oauth2.rfc6749.resource_protector import ResourceProtector, TokenValidator
from authlib.oauth2.rfc6750.errors import InsufficientScopeError, InvalidTokenError
from fastapi import HTTPException, Request
from joserfc import jwt
from joserfc.errors import JoseError

from app.auth.server import AUDIENCE, ISSUER, get_signing_key


class DemoJWTTokenValidator(TokenValidator):
    """Decodes and verifies JWTs minted by app.auth.server.issue_token."""

    def authenticate_token(self, token_string: str) -> dict[str, Any] | None:
        try:
            token = jwt.decode(token_string, get_signing_key())
        except JoseError:
            return None

        claims = token.claims
        if claims.get("iss") != ISSUER or claims.get("aud") != AUDIENCE:
            return None
        return claims

    def validate_token(
        self, token: dict[str, Any] | None, scopes: list[str], request: Request, **kwargs: Any
    ) -> None:
        if token is None:
            raise InvalidTokenError()
        if token.get("exp", 0) < time.time():
            raise InvalidTokenError()
        if scopes and self.scope_insufficient(token.get("scope"), scopes):
            raise InsufficientScopeError()


resource_protector = ResourceProtector()
resource_protector.register_token_validator(DemoJWTTokenValidator())


def require_scope(*scopes: str):
    """FastAPI dependency factory enforcing one or more SMART-style scopes.

    Returns the decoded token claims on success, so route handlers can
    read e.g. ``token["sub"]`` if useful for auditing.
    """

    async def _dependency(request: Request) -> dict[str, Any]:
        try:
            token = resource_protector.validate_request(list(scopes), request)
        except OAuth2Error as exc:
            headers = {"WWW-Authenticate": f'Bearer error="{exc.error}"'}
            raise HTTPException(
                status_code=exc.status_code, detail=exc.error, headers=headers
            ) from exc
        return token

    return _dependency
