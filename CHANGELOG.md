# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
per-package (each package is versioned independently).

## [Unreleased]

### Added

- `services/model-serving` (Python, FastAPI): work in progress toward
  Phase 4 (MLOps Kubernetes stack). So far: a demonstration
  splice-junction classifier (scikit-learn RandomForest over the UCI
  Molecular Biology splice-junction dataset, ~96% held-out accuracy,
  explicitly documented as a non-production demonstration model), an
  MLflow (SQLite-backed) tracking + Model Registry training/promotion
  pipeline, a FastAPI serving app that loads the promoted model as a
  self-contained artifact (no live MLflow dependency at request time),
  and a multi-stage Dockerfile verified end-to-end with real
  `docker build`/`docker run` (`/health`, `/model-info`, `/predict` all
  hit against the real container). 32 tests, ~95% coverage.

## [v0.3.0-jbrowse-plugin] - 2026-07-03

Phase 3: `plugins/jbrowse2-sv-tracks`, a JBrowse2 structural-variant arc plugin.

### Added

- `plugins/jbrowse2-sv-tracks/backend` (Python, Flask + pysam):
  - `sv_source.py`: parses VCF SV records (DEL/DUP/INV symbolic ALTs and
    BND breakend pairs) into a uniform breakpoint-pair JSON shape.
  - `GET /api/svs` and `/api/health` endpoints, CORS-enabled.
  - pytest suite (25 tests, 100% coverage, gated at 90%).
  - GitHub Actions CI (ruff/black/isort/mypy + pytest), verified in
    fresh Linux containers across Python 3.11/3.12.
- `plugins/jbrowse2-sv-tracks/plugin` (plain JavaScript, Rollup UMD bundle):
  - `SvJsonAdapter`: fetches SV records and builds JBrowse Features,
    with client-side region-overlap filtering so the same adapter works
    against either a live backend or a static JSON file.
  - `SvArcRenderer`: SVG bezier arcs between same-contig breakpoints
    (mirroring JBrowse2's own official "arc" plugin), or a marker +
    label for cross-contig BND (a linear view can't show both ends of
    those as a single arc — an explicit scope boundary, not a gap).
  - Reuses JBrowse's stock `FeatureTrack`/`LinearBasicDisplay` rather
    than a custom Track/Display type, since external UMD plugins can't
    statically import `@jbrowse/plugin-linear-genome-view` (not on
    JBrowse's re-export list for external plugins).
  - vitest suite (37 tests, 100% coverage across statements/branches/
    functions/lines), verified in fresh Node 20/22 Linux containers.
  - End-to-end verified against a real `@jbrowse/cli`-assembled
    jbrowse-web v4.3.0 via Puppeteer (not just a successful build) —
    found and fixed four real bugs invisible to unit tests: a
    `window.JBrowseExports` default-export shape mismatch for
    `FeatureRendererType`, a re-export subpath
    (`@jbrowse/core/util/simpleFeature`) that doesn't exist at runtime,
    a `ConfigurationSchema` default value that collided with real usage
    and collapsed the config snapshot to `{}`, and relative URLs
    breaking when adapter/renderer code runs inside an RPC web worker.
    Full writeup in `docs/blog-post.md`.
- `plugins/jbrowse2-sv-tracks/demo`: a static-JSON-backed GitHub Pages
  demo assembly (`build_static_svs.py` + `config.json`), deployed by
  `.github/workflows/jbrowse2-sv-tracks-pages.yml`.
- `plugins/jbrowse2-sv-tracks/workflow`: a Dockstore-compatible WDL
  workflow (`prepare_sv_track_data.wdl`) sorting/indexing a VCF and BAM,
  with a repo-root `.dockstore.yml`. Actually run end-to-end with
  miniwdl + real Docker containers, not just syntax-checked; caught a
  real bug (the `staphb/bcftools` image doesn't ship the standalone
  `tabix` binary — fixed with `bcftools index --tbi`). Not registered
  live on dockstore.org.
- Sample data: `backend/data/volvox.fa`/`volvox-sorted.bam` are real
  public data from GMOD/jbrowse-components' own test fixtures;
  `sv-demo.vcf` is hand-authored (no small public VCF with real SV
  records sharing coordinates with volvox was found) — both documented
  in `backend/data/DATA_SOURCE.md`.

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
    Postgres/Redis in CI. Coverage is configured with
    `concurrency = ["greenlet"]` so `coverage.py` correctly traces
    lines that resume after an awaited SQLAlchemy async ORM call —
    without it, those lines are intermittently reported as missed on
    Linux/Python 3.11-3.12 even though they run on every request.
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
