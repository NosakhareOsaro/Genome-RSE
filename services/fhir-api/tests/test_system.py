from __future__ import annotations

from httpx import AsyncClient


async def test_capability_statement_shape(client: AsyncClient):
    response = await client.get("/metadata")
    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "CapabilityStatement"
    assert body["fhirVersion"] == "4.0.1"
    assert body["rest"][0]["resource"][0]["type"] == "MolecularSequence"
    interactions = {i["code"] for i in body["rest"][0]["resource"][0]["interaction"]}
    assert {"read", "search-type", "create", "update", "delete"} <= interactions


async def test_capability_statement_requires_no_auth(client: AsyncClient):
    response = await client.get("/metadata")
    assert response.status_code == 200


async def test_healthz_ok(client: AsyncClient):
    response = await client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "time" in body
