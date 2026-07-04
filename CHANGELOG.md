# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
per-package (each package is versioned independently).

## [Unreleased]

Phase 5: original, externally-verifiable contributions building on Phases 1-4 (target tag `v1.1.0-original-contributions`).

### Added

- `contributions/01-jbrowse2-reexports-issue.md`: WP1, a real upstream bug
  report filed against GMOD/jbrowse-components
  ([#5594](https://github.com/GMOD/jbrowse-components/issues/5594), filed
  2026-07-04, open). Re-verified a Phase 3 finding (the `FeatureRendererType`
  default-export shape mismatch) against a freshly assembled, current
  jbrowse-web v4.3.0 -- not our own already-fixed plugin code -- mapped its
  full scope (4 of the affected base classes, not just 1), ruled out a
  source-level export-syntax explanation by comparing the wrapped and
  unwrapped modules' actual source, and confirmed it affects the officially
  recommended `jbrowse-plugin-template` tooling before filing. A related
  documentation PR (explaining `ConfigurationSchema`'s `postProcessSnapshot`
  collapse-to-`{}` behavior) is drafted but intentionally held pending a
  maintainer response to #5594.
- WP2: repo-root `LICENSE`, `CITATION.cff`, and `.zenodo.json`, ahead of a
  real Zenodo DOI mint once `v1.1.0-original-contributions` is tagged and
  released. Also fixes a previously undiscovered gap: there was no
  LICENSE file anywhere at the repo root, even though every package
  already independently declared MIT (`gh api repos/.../license`
  confirmed GitHub detected no license repo-wide).
- `contributions/02-dockstore-registration.md`: WP3, the Phase 3
  `prepare_sv_track_data.wdl` workflow (already verified end-to-end with
  real `miniwdl`/Docker execution) registered and published live on
  Dockstore
  ([prepare-sv-track-data](https://dockstore.org/workflows/github.com/NosakhareOsaro/Genome-RSE/prepare-sv-track-data:main?tab=info),
  2026-07-04). Troubleshot a real first-time-sync gotcha along the way:
  Dockstore's GitHub App sync is webhook-driven and doesn't retroactively
  scan a `.dockstore.yml` that predates app installation -- fixed by
  adding the workflow's `topic` field (a real, useful field, not a
  throwaway change) to produce the push Dockstore was waiting for.
- `contributions/03-pypi-publication.md`: WP4, `packages/py-genomics-utils`
  published for real to PyPI as
  [`genomerse-genomics-utils` 0.1.0](https://pypi.org/project/genomerse-genomics-utils/0.1.0/)
  (2026-07-04) -- `pip install genomerse-genomics-utils` genuinely works
  from the public internet. Renamed from the originally-available but
  too-generic `genomics-utils` (PyPI distribution name only; the Python
  import path stays `genomics_utils`) before any registry upload. Dry-run
  published to test.pypi.org first under the final name, then
  functionally verified in a fresh virtualenv (real `annotate_vcf()` and
  `validate_resource()` calls against real sample inputs, not just an
  import check) both after the test.pypi.org dry run and again after the
  real, irreversible `pypi.org` publish.

## [v1.0.0-mlops-stack] - 2026-07-03

Phase 4: `services/model-serving` + `infra/`, an MLOps Kubernetes stack.

### Added

- `services/model-serving` (Python, FastAPI):
  - A demonstration splice-junction classifier: scikit-learn
    `RandomForestClassifier` (50 trees, max depth 12) over one-hot
    encoded 60-nucleotide windows from the UCI Molecular Biology
    "Splice-junction Gene Sequences" dataset (real GenBank-derived
    primate DNA, cached in `data/`, provenance in `data/DATA_SOURCE.md`),
    ~96% held-out accuracy. Explicitly documented, in module docstrings
    and the service README, as a demonstration stand-in for an MLOps
    pipeline -- not a production or clinical splice-site predictor.
  - `training/train.py` + `training/promote_model.py`: an MLflow
    (SQLite-backed tracking store) training/Model Registry pipeline --
    every run genuinely registers a new model version and aliases a
    specific version as `production` via MLflow's real registry API.
  - `app/`: a FastAPI serving endpoint (`/health`, `/model-info`,
    `/predict`) that loads the promoted model as a self-contained,
    committed artifact (`app/model_artifact/`) with no live MLflow
    dependency at request time -- see `docs/adr/0001-*.md` and
    `docs/adr/0003-*.md` for the reasoning.
  - `app/features.py` one-hot encodes over the observed 8-symbol
    alphabet (ACGT plus 4 IUPAC ambiguity codes present in the dataset),
    shared by both training and serving so they can't silently drift.
  - A multi-stage `Dockerfile`, verified end-to-end with real `docker
    build`/`docker run` (not just a successful build) -- confirmed which
    copy of `app/` Python actually imports at runtime, and got correct
    real predictions from the running container.
  - pytest suite (32 tests, ~95% coverage, gated at 90%), verified in a
    fresh `python:3.12-slim` container reproducing CI's exact steps,
    including a full real `train -> register -> promote -> export` run
    (not just unit tests of isolated functions) that reproduced the same
    96.08% accuracy via a fixed random seed.
  - GitHub Actions CI: ruff/black/isort/mypy + pytest across Python
    3.11-3.12, plus the same real training-pipeline run as a CI step.
- `infra/k8s`: raw Kubernetes manifests (namespace, configmap,
  deployment with readiness/liveness probes, NodePort service) plus a
  `kind-config.yaml`. Actually deployed to a real local `kind` cluster --
  both replicas reached `Running`/`Ready`, with `/health`, `/model-info`,
  `/predict` all returning correct real responses through the cluster's
  NodePort, not just `kubectl apply --dry-run`.
- `infra/helm/model-serving`: a Helm chart templating the same
  deployment, parametrized via `values.yaml` (image repo/tag/pull
  policy, replicas, service, resources, probes). `helm lint`/`helm
  template` pass; `helm install` was verified against the same real
  local kind cluster with the same real responses.
- `.github/workflows/model-serving-cd.yml`: builds the image, pushes it
  to GHCR (via the workflow's own `GITHUB_TOKEN`, no extra secrets),
  creates a kind cluster in the CI runner, loads the just-built image
  directly (`kind load docker-image`), deploys with the Helm chart, and
  runs a real in-cluster `curl` validation against `/health` and
  `/predict` from a throwaway pod before tearing the cluster down. The
  full kind/helm/kubectl sequence was verified locally before being
  written into CI.
- `infra/terraform`: AWS IaC (S3 artifact bucket, ECR repository, IAM
  roles scoped to this project's own resources, AWS Batch Fargate
  compute environment/queue/job definition) as **infrastructure-as-code
  only** -- no AWS credentials, no remote backend, nothing applied.
  Verified with `terraform fmt -check` and `terraform validate`
  (`init -backend=false`); no `plan`/`apply` was run.
- `docs/adr`: three Architecture Decision Records -- FastAPI over Flask
  for model serving, Kubernetes/Helm over Docker Compose at this tier,
  and a database/cache technology choice carried over from Phase 2
  (SQLite now for MLflow's single-writer training use case, Postgres +
  Redis at real multi-user scale, for the same underlying reasoning
  Phase 2 used to choose them).

### Fixed

- `model-serving-cd.yml` failed on its first real run on GitHub's
  runners (post-tag, in `7aa1a33`): Docker rejected the image reference
  because `github.repository_owner` resolves to `NosakhareOsaro`
  (mixed case), and GHCR/Docker repository names must be all-lowercase.
  GitHub Actions expressions have no built-in `lower()`, so the fix
  moved `IMAGE` out of the static `env:` block and into a shell step
  that lowercases the owner with `tr` before building/pushing. Verified
  locally (the substitution genuinely produces
  `ghcr.io/nosakhareosaro/genome-rse-model-serving`) and confirmed
  green on the real repo's Actions runners afterward. All other
  `github.com/NosakhareOsaro/...` references elsewhere in this repo are
  plain URLs, which are case-insensitive, and didn't need the same fix.

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
    Linux/Python 3.11-3.12 even though they run on every request. Found
    when CI first ran the suite on a real Linux runner after local
    verification had already passed (macOS didn't reproduce the gap);
    fixed in `6f97aab`, a one-line `pyproject.toml` config change, no
    test logic was missing.
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
