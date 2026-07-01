# GenomeRSE

A research-software-engineering portfolio project demonstrating packaging, testing, CI/CD, and
documentation practices across a multi-phase bioinformatics tooling repository.

## Repository layout

- `packages/` — installable libraries (Python, R, ...)
- `services/` — deployable services
- `plugins/` — third-party tool integrations (later phase)
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

- **Phase 2** (`v0.2.0-fhir-api`, in progress): [`services/fhir-api`](services/fhir-api) —
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

Later phases will build on this foundation; this README will grow with each milestone.
