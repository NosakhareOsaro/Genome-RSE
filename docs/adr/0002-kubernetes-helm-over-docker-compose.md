# 0002: Why Kubernetes/Helm over Docker Compose at this tier

## Status

Accepted.

## Context

`services/fhir-api` (Phase 2) runs its full local stack -- API, Postgres,
Redis, Prometheus, Grafana -- via a single `docker compose up --build`.
That was the right call there: a fixed set of containers on one host,
with no requirement to demonstrate orchestration, scaling, or rollout
behavior. Phase 4 explicitly asks for a `kind`-deployable Kubernetes
manifest set plus a Helm chart instead. This ADR is about why the same
"simplest tool for the job" reasoning that picked Compose for Phase 2
picks Kubernetes/Helm here.

## Decision

Kubernetes + Helm, for reasons specific to what this phase needs to
demonstrate and exercise for real, not because it's more "advanced":

1. **The phase's explicit purpose is to demonstrate Kubernetes/Helm/CD
   competency** (see the top-level README's "target roles this
   demonstrates" section) -- for a research-software-engineering
   portfolio, showing a real, verified `kind` deployment and a real
   Helm chart is the point, not an accident of tooling.
2. **Declarative replica management and health-checked self-healing are
   real, exercised features here,** not just extra YAML: `infra/k8s/deployment.yaml`
   runs 2 replicas with `readinessProbe`/`livenessProbe` against
   `/health`, verified against a real local cluster (both pods reaching
   `Running`/`Ready` independently). Compose can restart a crashed
   container, but doesn't have a readiness-gated rolling deployment
   model.
3. **Helm's `values.yaml` parametrization is exercised for a genuine
   purpose:** the CD pipeline `--set`s a real GHCR image reference at
   deploy time (`infra/helm/model-serving/README.md`), while local
   development uses the same chart with its local-kind defaults. A
   single Compose file doesn't parametrize this way without a second
   templating layer bolted on.
4. **The CD pipeline needs an ephemeral, disposable, real cluster to
   validate against** (`.github/workflows/model-serving-cd.yml`) --
   `kind` gives that in CI in a way Compose (a single-host tool) doesn't
   map onto naturally.

## Consequences

- More moving parts than Compose: `kind`, `helm`, `kubectl`, plus the
  Helm chart's templating layer, versus one `docker-compose.yml`.
  `services/model-serving` deliberately ships **no** `docker-compose.yml`
  (see its README) -- a bare `docker run` is enough for a pre-Kubernetes
  smoke test, and adding Compose on top would just be a third deployment
  path to keep in sync with the other two.
- Judged purely on "run one container efficiently," this is
  over-engineered for a single stateless service with no peer services
  to orchestrate -- that tradeoff is accepted deliberately, for the
  reason in point 1 above, not overlooked.
- Two parallel deployment definitions now exist (`infra/k8s`'s raw
  manifests and `infra/helm`'s chart). Both were verified against the
  same real local cluster rather than assuming the Helm chart is
  "just" a template of the manifests; keeping both in sync is a real,
  accepted maintenance cost of documenting the plain-manifest path
  alongside the one the CD pipeline actually uses.
