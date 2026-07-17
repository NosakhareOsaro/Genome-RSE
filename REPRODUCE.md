# Reproducing GenomeRSE

This document gives step-by-step instructions for reproducing this project from scratch — the
four core phases plus the Phase 5 external contributions. It assumes working knowledge of Python,
R, JavaScript, Git, Docker, and Kubernetes, and covers every command, configuration file, and
verification step involved.

## Prerequisites

- Python 3.11+ and 3.12 (for cross-version testing)
- R 4.x with `devtools`, `usethis`, `testthat`, `roxygen2`, `pkgdown`, `covr` installed
- Node.js 20+ and npm
- Docker Desktop (with Kubernetes support, or a working `kind` installation)
- `kubectl`, `kind`, `helm` CLI tools
- `terraform` CLI
- Accounts on: GitHub, PyPI, test.pypi.org, Zenodo, Dockstore

## Repository setup

```bash
mkdir GenomeRSE && cd GenomeRSE
git init
git config user.name "Your Name"
git config user.email "your@email.com"
```

Create the top-level structure:

```bash
mkdir -p packages services plugins infra docs contributions .github/workflows
```

Create a `.gitignore` covering Python (`__pycache__/`, `*.pyc`, `.venv/`), R (`.Rproj.user/`,
`.Rhistory`), Node (`node_modules/`), Docker/Terraform build artifacts, and secrets (`.env`,
`*.tfstate`).

Add a root `LICENSE` file (MIT or your preferred license) and a `CITATION.cff` file following the
[Citation File Format spec](https://citation-file-format.github.io/) — this is what GitHub's "Cite
this repository" feature and Zenodo both read.

---

## Phase 1: Packaged libraries

### Python package

```bash
mkdir -p packages/py-genomics-utils/src/genomics_utils/multiqc_plugin
mkdir -p packages/py-genomics-utils/tests/data
cd packages/py-genomics-utils
```

Write `pyproject.toml` (PEP 621 format) declaring:

- `name`, `version`, dependencies: `pydantic>=2.0,<3.0`, `multiqc>=1.21,<2.0`
- `[project.optional-dependencies].dev`: `pytest`, `pytest-cov`, `black`, `ruff`, `isort`, `mypy`, `pre-commit`
- `[tool.pytest.ini_options]` pointing `testpaths` at `tests`
- `[tool.coverage.run]` with `source = ["genomics_utils"]`, `branch = true`
- `[project.entry-points."multiqc.modules.v1"]` registering the MultiQC module

Implement `src/genomics_utils/vcf_annotate.py`:

- A function reading a VCF file line by line, skipping `#`-prefixed header lines
- Classify each variant by comparing REF/ALT allele lengths: equal length + 1bp = SNP, REF longer
  = deletion, ALT longer = insertion
- For SNPs, classify as transition (A↔G or C↔T) or transversion (any other substitution)
- Return a summary object with per-type counts and the transition/transversion ratio

Implement `src/genomics_utils/fhir_validate.py`:

- Pydantic models for a minimal FHIR R4 `Patient` and `Observation` resource (reference: HL7's FHIR
  R4 specification, `hl7.org/fhir/R4`)
- A `validate_resource(json_dict)` function instantiating the appropriate model and catching
  `pydantic.ValidationError`, returning `(is_valid, errors)`

Implement `src/genomics_utils/multiqc_plugin/genomics_module.py`:

- A class subclassing MultiQC's `BaseMultiqcModule`
- Search for `*_genomics_utils.json` files, parse them, and add a results table/plot to the report

Write tests in `tests/`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --cov=genomics_utils --cov-report=term-missing
```

Iterate until coverage exceeds 90%. Set up `.pre-commit-config.yaml` running `black`, `ruff`,
`isort`, and `mypy` on every commit.

### R package

```bash
cd ../../
Rscript -e 'usethis::create_package("packages/r-rnaseq-wrapper")'
```

Implement functions under `R/`: loading a count matrix from CSV, normalizing it, running a basic
differential-expression comparison, and plotting results. Document each with `roxygen2` comments
(`#'` blocks above each function), then run:

```r
devtools::document()
devtools::test()
covr::package_coverage()
devtools::check()
```

Add `pkgdown::build_site()` configuration (`_pkgdown.yml`) and a `README.Rmd`.

### CI

Write `.github/workflows/py-genomics-utils-ci.yml` and `r-rnaseq-wrapper-ci.yml`: on push, run a
matrix over Python 3.11/3.12 (lint + pytest) and `r-lib/actions/setup-r` + `check-r-package` for R.

---

## Phase 2: FHIR REST API

```bash
mkdir -p services/fhir-api/app/{models,auth,routers} services/fhir-api/{alembic,tests,monitoring,loadtest}
```

**Models.** In `app/models/orm.py`, a SQLAlchemy ORM class for `MolecularSequence` with indexed
columns (id, patient reference) plus a full JSON payload column. In `app/models/fhir.py`, a
Pydantic model for the FHIR R4 `MolecularSequence` resource shape.

**Database.** `app/db.py` sets up an async SQLAlchemy engine via `asyncpg`. Initialize Alembic
(`alembic init alembic`), configure `env.py` for async migrations, and generate the initial
migration: `alembic revision --autogenerate -m "create molecular_sequences"`.

**Auth.** In `app/auth/server.py`, implement an OAuth2 `client_credentials` grant (per RFC 6749)
issuing JWTs signed with `joserfc`. In `app/auth/security.py`, a FastAPI dependency validating
bearer tokens and checking scopes on protected routes.

**Caching & rate limiting.** `app/cache.py` wraps `redis.asyncio` in cache-aside helpers. Wire
`slowapi`'s `Limiter` into `app/main.py` and decorate routes with rate limits.

**Metrics.** `app/metrics.py` defines Prometheus `Counter`/`Histogram` objects and exposes them at
`/metrics`. Write `monitoring/prometheus.yml` and a Grafana dashboard JSON under
`monitoring/grafana/`.

**Routers.** `app/routers/molecular_sequence.py` implements FHIR RESTful create/read/search/
update/delete for `MolecularSequence`. `app/routers/system.py` implements `/metadata`
(CapabilityStatement) and `/healthz`.

**Tests.** Use `httpx.AsyncClient` against the FastAPI app, an in-memory SQLite database via
`aiosqlite` with `StaticPool`, and `fakeredis` — no live Postgres/Redis needed for CI speed.
Configure `pytest-asyncio` with `asyncio_mode = "auto"`.

**Coverage gotcha.** If coverage on Linux CI comes in lower than expected, with missing lines
sitting immediately after `await session.xxx()` calls, add to `pyproject.toml`:

```toml
[tool.coverage.run]
concurrency = ["greenlet"]
```

This tells `coverage.py` to trace across the greenlet-based context switches SQLAlchemy's async
engine uses internally — without it, lines that run on every request can be misreported as missed.

**Containerization.** Write a multi-stage `Dockerfile` and a `docker-compose.yml` wiring together
`api`, `postgres`, `redis`, `prometheus`, and `grafana`. Verify with `docker compose up --build`
and real `curl` requests against `/health`, `/metadata`, and the CRUD endpoints.

**Load testing.** Write a `locustfile.py` exercising token issuance followed by CRUD/search
requests.

---

## Phase 3: JBrowse2 plugin

```bash
mkdir -p plugins/jbrowse2-sv-tracks/{backend,plugin,demo,workflow,docs}
```

**Backend.** A small Flask app (`backend/app.py`) with `/api/health` and `/api/svs` endpoints.
`backend/sv_source.py` uses `pysam` to parse structural-variant records (symbolic ALTs like `<DEL>`/
`<DUP>`/`<INV>`, and `BND` breakend pairs) from a VCF into a uniform JSON shape.

**Sample data.** Use JBrowse2's own public `volvox` test genome/BAM as real reference data (cited
in a `DATA_SOURCE.md`). Since no small public VCF contains real structural variants on this
reference, hand-author a small synthetic SV VCF and document that explicitly.

**Plugin scaffold.** Clone GMOD's official `jbrowse-plugin-template` as a starting point. It uses
Rollup (`rollup.config.mjs`) to bundle the plugin as a UMD module, mapping imports from
`@jbrowse/core/...` onto `window.JBrowseExports` via `rollup-plugin-external-globals` (a mechanism
that lets external plugins reuse JBrowse2's own internals without bundling a second copy).

**Adapter and renderer.** `plugin/src/SvJsonAdapter/index.js` fetches from the Flask backend and
builds JBrowse `Feature` objects. `plugin/src/LinearSvArcDisplay/` implements a custom SVG renderer
drawing bezier arcs between same-contig breakpoints, and a labeled marker with a link for
cross-contig (`BND`) events.

**Runtime verification.** Assemble a real JBrowse2 instance: `npx @jbrowse/cli create ./jbrowse-web`.
Serve it locally and load the built plugin. Open the browser console and inspect
`window.JBrowseExports` directly — do not assume the build succeeding means the plugin works at
runtime, since some internal exports may be wrapped in `{ default: ... }` inconsistently, which
throws `Class extends value #<Object> is not a constructor or null` only when actually loaded in a
browser, invisible to both the build and unit tests (which import from the real npm package, where
this doesn't occur).

Automate this check with Puppeteer: launch a real headless Chrome instance, load the assembled
page, wait for rendering, and query the DOM directly for the expected number of arc/marker
elements, capturing any console errors.

**WDL workflow.** Write `workflow/prepare_sv_track_data.wdl` sorting and indexing the VCF/BAM using
`samtools`/`bcftools` inside a Docker container, specified per WDL's task/workflow syntax. Add a
root `.dockstore.yml` describing it. Run it end-to-end locally with `miniwdl run` before trusting
it.

**GitHub Pages demo.** Build a static-JSON snapshot of the SV data (no live backend needed for the
public demo), assemble a static `jbrowse-web` build, and write a GitHub Actions workflow using
`actions/upload-pages-artifact` and `actions/deploy-pages` to publish it. Note: GitHub Pages must be
enabled once, manually, in the repository's Settings → Pages, with source set to "GitHub Actions."

---

## Phase 4: MLOps Kubernetes stack

```bash
mkdir -p services/model-serving/{app,training,data,tests} infra/{k8s,helm/model-serving,terraform} docs/adr
```

**Data and training.** Cache the UCI "Splice-junction Gene Sequences" dataset. Write
`training/features.py` one-hot encoding 60-nucleotide DNA windows over the observed nucleotide
alphabet. Write `training/train.py` training a `scikit-learn` `RandomForestClassifier`, logging
parameters/metrics/the model itself to MLflow (`mlflow.start_run()`, `mlflow.sklearn.log_model()`),
using a local SQLite-backed tracking URI (`sqlite:///mlflow.db`), and registering the trained model
in MLflow's Model Registry.

**Promotion.** Write `training/promote_model.py` that aliases a specific registered model version
as `production` and exports it as a committed artifact under `app/model_artifact/` — serving loads
this directly, decoupled from a live MLflow server at request time.

**Serving.** A FastAPI app (`app/main.py`) with `/health`, `/model-info`, `/predict` endpoints
loading the bundled model artifact.

**Containerization.** A multi-stage `Dockerfile`. Verify with real `docker build`/`docker run` and
`curl` against all three endpoints before moving on.

**Kubernetes.** Write raw manifests (`infra/k8s/`: namespace, configmap, deployment with
readiness/liveness probes, service) and a `kind-config.yaml`. Create a local cluster
(`kind create cluster --config infra/k8s/kind-config.yaml`), load the built image
(`kind load docker-image`), `kubectl apply` the manifests, and confirm pods reach `Ready` with real
`curl` responses through the service.

**Helm.** Convert the manifests into a parametrized Helm chart (`infra/helm/model-serving/`) with
`values.yaml` controlling image, replicas, resources, and probes. Verify with `helm lint`,
`helm template`, and a real `helm install` against the same local cluster.

**CI/CD.** Write a GitHub Actions workflow: build the image, push to `ghcr.io` (note: the image tag
must be lowercase — if using `${{ github.repository_owner }}` to construct it, explicitly lowercase
it with a shell step like `tr '[:upper:]' '[:lower:]'`, since Docker rejects uppercase registry
paths), spin up a `kind` cluster inside the runner, load the image, deploy via Helm, run an
in-cluster `curl` validation from a throwaway pod, then tear the cluster down.

**Terraform (IaC only).** Write `.tf` files describing an S3 bucket, ECR repository, IAM roles, and
an AWS Batch compute environment/queue/job definition. Validate with
`terraform init -backend=false`, `terraform validate`, and `terraform fmt -check` — do not run
`terraform apply` unless you intend to provision real, billable cloud resources.

**ADRs.** Write short Architecture Decision Records under `docs/adr/` for each significant,
non-obvious technical choice (e.g., why FastAPI over Flask, why Kubernetes/Helm over Docker Compose
at this tier).

---

## Phase 5: External contributions

### Filing an upstream issue

Re-verify any suspected upstream bug against the current released version of the affected project
— assemble it fresh, don't assume an earlier finding still holds. Map the bug's full scope
precisely (which specific classes/modules are affected). Search the project's existing issue
tracker for prior reports. Write a reproducible report: environment, exact reproduction steps,
expected vs. actual behavior, and impact. File it via the project's GitHub "New Issue" form.

### Registering on Dockstore

Ensure a valid `.dockstore.yml` exists at the repository root (schema documented at
`docs.dockstore.org`). Install Dockstore's GitHub App (`dockstore.org` → login → "Manage Dockstore
Installations on GitHub"), granting it access to the repository. If the workflow doesn't appear
under "My Workflows" after a manual refresh, check the GitHub App's sync logs on Dockstore's own
site — an empty log means sync was never triggered (rather than failing), which typically requires
a fresh commit to the repository after installation to fire the first webhook. Once it appears,
publish it from its detail page.

### Publishing to PyPI

Check name availability directly against PyPI's Simple API
(`https://pypi.org/simple/<name>/`, a 404 means available) rather than the human-facing search
page. Build the package (`python -m build`) and validate it (`twine check dist/*`). Register a
separate account at `test.pypi.org`, generate an API token there, and rehearse the full publish
(`twine upload --repository testpypi dist/*`), then install it into a fresh virtual environment
using `--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/` (since
test.pypi.org doesn't mirror real dependencies) and call its actual functions to confirm it works,
not just that it imports. Only then register a real PyPI account, generate a real token, and run
`twine upload dist/*` — irreversible, since a published name+version can never be deleted and
reused.

### Archiving with Zenodo

Add `CITATION.cff` and `.zenodo.json` at the repository root. Log into `zenodo.org` via GitHub
OAuth, go to Account Settings → GitHub, and toggle the repository on — this installs a webhook that
fires on release-publish events. Publish a GitHub Release from a tag. If no DOI appears after a few
minutes, check the repository's own Settings → Webhooks → the Zenodo webhook's "Recent Deliveries"
on GitHub directly — if the toggle was switched on after an earlier release was already published,
that release was never sent to Zenodo, and a fresh release needs to be published now that the
connection is genuinely active.

### Writing the case study

Summarize each of the above in a document written for a reader unfamiliar with the specific tools
involved: what the underlying gap or task was, what was done, the real external artifact produced
(with a direct link), and what it demonstrates — being explicit that none of it constitutes novel
research, only standard engineering practice carried out with genuine external verification at
each step.

---

## Final verification checklist

Before considering any phase complete:

- [ ] Full test suite passes in a fresh, disposable environment matching CI exactly (not just
      locally)
- [ ] Coverage meets the configured threshold, measured the same way CI measures it
- [ ] Any live deployment target (Docker Compose stack, Kubernetes cluster, Pages site) is actually
      exercised end-to-end, not just assumed to work from configuration alone
- [ ] No placeholder URLs, fake credentials, or unresolved TODOs remain
- [ ] Every external artifact (issue, DOI, package page, workflow registration) resolves and is
      publicly accessible
