# Architecture Decision Records

Short records of significant, non-obvious technical decisions and the
reasoning behind them -- not a full design doc, just enough context for
someone (including future us) to understand *why*, not just *what*.

Format: Status / Context / Decision / Consequences, one file per
decision, numbered in the order they were written.

- [0001](0001-fastapi-over-flask-for-model-serving.md) -- Why FastAPI over Flask for model serving
- [0002](0002-kubernetes-helm-over-docker-compose.md) -- Why Kubernetes/Helm over Docker Compose at this tier
- [0003](0003-sqlite-now-postgres-redis-at-scale.md) -- Database/cache technology choice (carried over from Phase 2)
