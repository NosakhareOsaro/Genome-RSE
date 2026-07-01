"""Prometheus instrumentation, exposing GET /metrics.

Uses prometheus-fastapi-instrumentator's defaults: request counts
(`http_requests_total`), latency histograms
(`http_request_duration_seconds_bucket`), and request/response sizes,
all labeled by handler/method/status. The Grafana dashboard in
monitoring/ graphs these exact metric names.
"""

from __future__ import annotations

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def instrument_app(app: FastAPI) -> None:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
