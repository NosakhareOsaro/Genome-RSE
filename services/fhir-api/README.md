# fhir-api

An async FastAPI service exposing a FHIR R4 `MolecularSequence` REST
interface, with SMART-style OAuth2, Redis caching, rate limiting, and
Prometheus metrics. Phase 2 of the GenomeRSE portfolio project.

> ## ⚠️ This is a demo Authorization Server — not a real EHR/IdP
>
> The OAuth2 token endpoint (`POST /oauth/token`) is a **self-contained
> demo Authorization Server** built with Authlib, issuing its own JWTs
> for a single hardcoded demo client via the `client_credentials` grant.
> It is **not connected to any real EHR, identity provider, or SMART on
> FHIR launch sequence**. All client secrets and signing keys shipped in
> this repo (`.env.example`, tests) are obvious placeholders
> (`REPLACE_ME_NOT_A_REAL_SECRET`) — replace them with real generated
> values before running this anywhere beyond local development, and do
> not treat this auth flow as production-grade identity infrastructure.
> See [`app/auth/`](app/auth) for implementation details.

## Status

This README grows alongside the implementation (see the repo-root
CHANGELOG for what has landed so far). Sections below will fill in as
each part of the service is built.

## Components

- **FHIR `MolecularSequence` REST API** — see `app/routers/`.
- **OAuth2 / auth** — see `app/auth/` and the callout above.
- **Caching** — see `app/cache.py`.
- **Rate limiting** — see `app/rate_limit.py`.
- **Metrics** — see `app/metrics.py` and `monitoring/`.

## Local development

```bash
cp .env.example .env   # then edit values as needed
pip install -e ".[dev]"
```

Full stack (API + Postgres + Redis + Prometheus + Grafana):

```bash
docker compose up --build
```
