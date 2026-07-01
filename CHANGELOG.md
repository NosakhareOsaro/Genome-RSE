# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
per-package (each package is versioned independently).

## [Unreleased]

## [v0.2.0-fhir-api] - 2026-07-01

Phase 2: `services/fhir-api`, an async FHIR R4 MolecularSequence REST API.

### Added

- `services/fhir-api` (Python, FastAPI, async):
  - FHIR R4 `MolecularSequence` REST API: create/read/search/update/delete,
    search returns a `searchset` Bundle, `/metadata` CapabilityStatement,
    `/healthz`. Minimal structural resource subset (same scope-limited
    approach as Phase 1's FHIR validator).
  - Self-contained demo OAuth2 Authorization Server (`client_credentials`
    grant, Authlib + joserfc JWTs) and Authlib `ResourceProtector`-based
    scope enforcement (`system/MolecularSequence.read`/`.write`).
    **Not connected to any real EHR/IdP** — loudly documented as a demo
    in the service README, module docstrings, and `.env.example`.
  - Async SQLAlchemy + asyncpg + Postgres, with an ORM design storing
    indexed search columns alongside the full resource as JSON; Alembic
    migrations (async-aware `env.py`), verified against a real ephemeral
    Postgres container.
  - Redis cache-aside layer for reads, with explicit invalidation on
    write/delete (not TTL-only).
  - Global rate limiting via slowapi (`Limiter(default_limits=...)` +
    `SlowAPIMiddleware`).
  - Prometheus `/metrics` (prometheus-fastapi-instrumentator) plus a
    provisioned Grafana dashboard (request rate, 5xx rate, p95 latency,
    total requests) and datasource.
  - pytest-asyncio suite (41 tests, 100% coverage, gated at a 95%
    minimum), using in-memory SQLite + fakeredis rather than live
    Postgres/Redis in CI.
  - GitHub Actions CI: ruff/black/isort/mypy + pytest across Python
    3.11-3.12.
  - Locust load-test script exercising token issuance + CRUD/search.
  - Multi-stage `Dockerfile` and a one-command `docker compose up --build`
    stack (api + postgres + redis + prometheus + grafana); Prometheus/
    Grafana config is baked into custom images at build time rather than
    bind-mounted, for portability across host file-sharing setups.
    Verified end-to-end against the real containers (not test doubles).
  - `docs/deployment.md`: AWS EC2 + Nginx + Let's Encrypt deployment
    guide (documentation only, no live infrastructure provisioned).
- `.env.example` for `fhir-api` with obviously-fake placeholder secrets
  (`REPLACE_ME_NOT_A_REAL_SECRET`).

## [v0.1.0-pypi-package] - 2026-07-01

Phase 1: two packages, each fully tested, documented, and CI-checked.

### Added

- Repository scaffold: top-level `packages/`, `services/`, `plugins/`, `infra/`, `docs/` directories.
- `.gitignore` covering Python, R, Docker, IDE, and OS artifacts.
- `packages/py-genomics-utils` (Python, PEP 621):
  - VCF annotation helper (`vcf_annotate`): variant classification
    (SNP/INS/DEL/MNV) and Ts/Tv summary statistics.
  - Minimal FHIR R4 resource validator (`fhir_validate`): structural
    validation of a `Patient`/`Observation` subset (explicitly not
    conformance-grade — see module docs).
  - MultiQC plugin (`multiqc_plugin`): a real `multiqc.modules.v1` module
    plus `multiqc.hooks.v1` search-pattern registration, visualizing the
    VCF annotation summary.
  - pytest suite (42 tests, 100% coverage, gated at a 90% minimum).
  - GitHub Actions CI: ruff/black/isort/mypy + pytest across Python
    3.10-3.12.
  - Sphinx docs (autodoc, napoleon, intersphinx) with a repo-root
    `.readthedocs.yaml`.
  - pre-commit config (black, ruff, isort, mypy).
  - `CITATION.cff` and a `.zenodo.json` scaffold.
- `packages/r-rnaseq-wrapper` (R):
  - Basic RNA-seq workflow: `load_counts()`, `normalize_counts()`
    (CPM/log2CPM), `run_deg()` (per-gene Welch t-test with
    Benjamini-Hochberg adjustment), `plot_results()` (volcano plot).
  - roxygen2-documented; testthat suite (31 tests, 97.7% coverage via
    covr).
  - pkgdown site config (`_pkgdown.yml`) and a README with a Codecov
    badge.
  - GitHub Actions R CMD check workflow (r-lib/actions).
- Sample data provenance documented for both packages: synthetic,
  hand-authored fixtures for VCF/count-matrix data, and official HL7
  FHIR R4 example resources for the FHIR fixtures.
