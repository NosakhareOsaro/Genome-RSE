from __future__ import annotations

import time

from httpx import AsyncClient, Response
from joserfc import jwt

from app.auth.server import AUDIENCE, ISSUER, get_signing_key
from tests.conftest import DEMO_CLIENT_ID, DEMO_CLIENT_SECRET


async def request_token(client: AsyncClient, **overrides: str) -> Response:
    data = {
        "grant_type": "client_credentials",
        "client_id": DEMO_CLIENT_ID,
        "client_secret": DEMO_CLIENT_SECRET,
    }
    data.update(overrides)
    return await client.post("/oauth/token", data=data)


async def test_issue_token_default_scope(client: AsyncClient):
    response = await request_token(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["scope"] == "system/MolecularSequence.read"
    assert body["expires_in"] == 3600
    assert isinstance(body["access_token"], str) and body["access_token"]


async def test_issue_token_explicit_scope(client: AsyncClient):
    response = await request_token(
        client, scope="system/MolecularSequence.write system/MolecularSequence.read"
    )
    assert response.status_code == 200
    assert response.json()["scope"] == "system/MolecularSequence.read system/MolecularSequence.write"


async def test_issue_token_wrong_client_id(client: AsyncClient):
    response = await request_token(client, client_id="someone-else")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_client"


async def test_issue_token_wrong_secret(client: AsyncClient):
    response = await request_token(client, client_secret="wrong")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_client"


async def test_issue_token_unsupported_grant_type(client: AsyncClient):
    response = await request_token(client, grant_type="password")
    assert response.status_code == 400
    assert response.json()["error"] == "unsupported_grant_type"


async def test_issue_token_invalid_scope(client: AsyncClient):
    response = await request_token(client, scope="system/*.write")
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_scope"


async def test_protected_endpoint_without_token(client: AsyncClient):
    response = await client.get("/MolecularSequence/does-not-matter")
    assert response.status_code == 401
    assert response.json()["detail"] == "missing_authorization"


async def test_protected_endpoint_garbage_token(client: AsyncClient):
    response = await client.get(
        "/MolecularSequence/does-not-matter", headers={"Authorization": "Bearer not-a-jwt"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid_token"


async def test_protected_endpoint_insufficient_scope(
    client: AsyncClient, read_only_headers: dict[str, str]
):
    response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_only_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "insufficient_scope"


async def test_protected_endpoint_expired_token(client: AsyncClient):
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": DEMO_CLIENT_ID,
        "scope": "system/MolecularSequence.read",
        "iat": now - 7200,
        "exp": now - 3600,
    }
    expired_token = jwt.encode({"alg": "HS256"}, claims, get_signing_key())

    response = await client.get(
        "/MolecularSequence/does-not-matter",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid_token"


async def test_protected_endpoint_wrong_issuer(client: AsyncClient):
    now = int(time.time())
    claims = {
        "iss": "someone-else",
        "aud": AUDIENCE,
        "sub": DEMO_CLIENT_ID,
        "scope": "system/MolecularSequence.read",
        "iat": now,
        "exp": now + 3600,
    }
    token = jwt.encode({"alg": "HS256"}, claims, get_signing_key())

    response = await client.get(
        "/MolecularSequence/does-not-matter", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid_token"
