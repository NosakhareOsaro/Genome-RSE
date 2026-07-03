# GenomeRSE

A research-software-engineering portfolio project demonstrating packaging, testing, CI/CD, and
documentation practices across a multi-phase bioinformatics tooling repository.

## Repository layout

- `packages/` — installable libraries (Python, R, ...)
- `services/` — deployable services
- `plugins/` — third-party tool integrations
- `infra/` — infrastructure-as-code (later phase)
- `docs/` — repository-wide documentation (later phase)

## Phases

- **Phase 1** (`v0.1.0-pypi-package`, done): two Phase 1 packages, each with
  its own test suite, CI workflow, docs, and packaging metadata:
  - [`packages/py-genomics-utils`](packages/py-genomics-utils) — a Python
    package with a VCF annotation helper, a minimal FHIR R4 resource
    validator, and a MultiQC plugin. PEP 621 packaging, pytest (100%
    coverage, gated at 90%), Sphinx/autodoc docs, pre-commit
    (black/ruff/isort/mypy), and CITATION.cff/.zenodo.json scaffolds.
  - [`packages/r-rnaseq-wrapper`](packages/r-rnaseq-wrapper) — an R package
    wrapping a basic RNA-seq differential expression workflow.
    roxygen2-documented, testthat suite (97.7% coverage via covr),
    pkgdown site config, and an R CMD check GitHub Actions workflow.

  Both packages use small, clearly-documented sample data (synthetic or
  official public spec examples — see each package's `tests/data/` or
  `inst/extdata/` provenance notes) and flag any simplified/non-conformance-
  grade scope directly in their docs.

- **Phase 2** (`v0.2.0-fhir-api`, done): [`services/fhir-api`](services/fhir-api) —
  an async FastAPI service exposing a FHIR R4 `MolecularSequence` REST
  API, with a self-contained demo OAuth2 Authorization Server (Authlib
  + joserfc; **not** a real EHR/IdP — see the service README's callout),
  async SQLAlchemy/asyncpg + Postgres, Redis cache-aside caching,
  slowapi rate limiting, Prometheus metrics with a provisioned Grafana
  dashboard, a pytest-asyncio suite (100% coverage, gated at 95%), a
  Locust load-test script, and a one-command `docker compose up --build`
  stack (verified end-to-end against real Postgres/Redis/Prometheus/
  Grafana). Deployment docs (AWS EC2 + Nginx + Let's Encrypt) are
  documentation-only — no live infrastructure is provisioned by this repo.

- **Phase 3** (`v0.3.0-jbrowse-plugin`, in progress): [`plugins/jbrowse2-sv-tracks`](plugins/jbrowse2-sv-tracks) —
  a JBrowse2 plugin rendering structural-variant arcs from VCF data
  (plain JavaScript, Rollup UMD bundle), backed by a small Flask +
  pysam REST API (`backend/`). Includes a Dockstore-compatible WDL
  workflow for preparing VCF/BAM data and a GitHub Pages live demo
  (static-JSON backed, no live server needed). Verified end-to-end
  against a real `@jbrowse/cli`-assembled jbrowse-web instance via
  Puppeteer — this caught four platform-specific bugs (JBrowseExports
  shape mismatches, a config-schema default collapse, and relative
  URLs breaking inside RPC workers) invisible to unit tests and the
  build alone; see the package README and `docs/blog-post.md` for the
  full writeup.

Later phases will build on this foundation; this README will grow with each milestone.
