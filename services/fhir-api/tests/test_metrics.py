from __future__ import annotations

from httpx import AsyncClient


async def test_metrics_endpoint_exposes_prometheus_text(client: AsyncClient):
    await client.get("/metadata")

    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds_bucket" in response.text


async def test_metrics_not_in_openapi_schema(client: AsyncClient):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "/metrics" not in response.json()["paths"]
