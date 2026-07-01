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
> this repo (`.env.example`, tests, `docker-compose.yml`) are obvious
> placeholders (`REPLACE_ME_NOT_A_REAL_SECRET`) — replace them with real
> generated values before running this anywhere beyond local
> development, and do not treat this auth flow as production-grade
> identity infrastructure. See [`app/auth/`](app/auth) for
> implementation details.

## API surface

- `POST /oauth/token` — client_credentials token issuance (see callout above)
- `GET /metadata` — FHIR CapabilityStatement (unauthenticated)
- `GET /healthz` — liveness/readiness check, includes a real DB query (unauthenticated)
- `GET /metrics` — Prometheus exposition format (unauthenticated)
- `POST /MolecularSequence` — create (scope: `system/MolecularSequence.write`)
- `GET /MolecularSequence/{id}` — read (scope: `system/MolecularSequence.read`)
- `GET /MolecularSequence?patient=...&_count=...` — search, returns a FHIR `searchset` Bundle (scope: `read`)
- `PUT /MolecularSequence/{id}` — full update (scope: `write`)
- `DELETE /MolecularSequence/{id}` — delete (scope: `write`)

## Design notes

**Storage: indexed columns + full JSON payload.** The ORM row
(`app/models/orm.py`) stores a couple of columns that the search API
actually filters on (`patient_reference`, `coordinate_system`)
alongside the complete FHIR resource as a JSON blob. Reads return the
exact resource that was written, byte-for-byte, while the DB can still
index/filter on the fields that matter. The tradeoff: those fields are
duplicated (once as a column, once inside the JSON), and adding a new
*searchable* field later needs a migration even though adding a new
*resource* field never does. This mirrors the same deliberate choice
made in Phase 1's `r-rnaseq-wrapper` for a different storage problem.

**Caching is cache-aside with explicit invalidation, not TTL-only.**
`GET /MolecularSequence/{id}` checks Redis first and populates it on a
miss; `PUT`/`DELETE` explicitly delete the cache entry rather than
waiting for the TTL to expire, so a read immediately after a write
never serves stale data (see `app/cache.py` and `tests/test_cache.py`
for the exact behavior this guarantees).

**Monitoring config is baked into images, not bind-mounted.**
`monitoring/prometheus.Dockerfile` and `monitoring/grafana.Dockerfile`
`COPY` their config at build time rather than the more common
bind-mount-from-host approach. This was a deliberate choice after
hitting a macOS Docker Desktop file-sharing permission error on a bind
mount under this project's path — baking the config in avoids that
whole class of host-permission issue and keeps `docker compose up
--build` portable across machines/CI with zero setup.

## Local development

```bash
cp .env.example .env   # then edit values as needed
pip install -e ".[dev]"
pytest                 # 100% coverage, gated at 95%; uses in-memory SQLite + fakeredis
```

## Full stack (one command)

```bash
docker compose up --build
```

Brings up: `api` (:8000), `postgres` (internal only), `redis` (internal
only), `prometheus` (:9090), `grafana` (:3000, anonymous viewer access
enabled for convenience -- login as `admin`/the `GF_SECURITY_ADMIN_PASSWORD`
placeholder for admin access). Postgres/Redis are intentionally not
published to the host to avoid colliding with services you may already
be running locally on their default ports; use `docker compose exec
postgres psql -U fhir` for ad-hoc access.

Try it:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/oauth/token \
  -d "grant_type=client_credentials&client_id=demo-client&client_secret=REPLACE_ME_NOT_A_REAL_SECRET&scope=system/MolecularSequence.read system/MolecularSequence.write" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/MolecularSequence \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"coordinateSystem": 0, "type": "dna"}'
```

## Load testing

```bash
pip install -e ".[loadtest]"
locust -f loadtest/locustfile.py --host http://localhost:8000
```

## Deployment

See [`docs/deployment.md`](docs/deployment.md) for documentation-only
guidance on deploying to AWS EC2 behind Nginx with Let's Encrypt (no
live infrastructure is provisioned by this repo).
