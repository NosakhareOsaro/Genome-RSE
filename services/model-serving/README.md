# model-serving

A FastAPI serving endpoint for a small splice-junction classifier,
trained and versioned through an MLflow Model Registry workflow and
deployed to Kubernetes (`infra/k8s`, `infra/helm`). Phase 4 of the
GenomeRSE portfolio project.

> ## ⚠️ Demonstration classifier, not a production splice-site predictor
>
> `training/train.py` fits a small `RandomForestClassifier` (50 trees,
> max depth 12) over one-hot encoded 60-nucleotide windows from the
> classic UCI "Molecular Biology (Splice-junction Gene Sequences)"
> dataset (see [`data/DATA_SOURCE.md`](data/DATA_SOURCE.md)). It scores
> ~96% accuracy on a held-out split of that small, clean benchmark. Real
> splice-site prediction (e.g. SpliceAI) uses deep CNNs over far larger
> genomic context and is validated against genome-scale, clinically
> relevant benchmarks. This model exists to demonstrate an MLOps
> pipeline end to end — train, register, promote, containerize, deploy —
> not to make a genuine research or clinical claim about splice-site
> prediction. Every place this model is referenced (module docstrings,
> this README, `docs/adr/`) repeats that scope explicitly.

## API surface

- `GET /health` — liveness check (unauthenticated)
- `GET /model-info` — the promoted model's registry name/version/run id/metrics
- `POST /predict` — `{"sequence": "<60 nucleotides>"}` → predicted class
  (`EI`/`IE`/`N`) and per-class probabilities. Rejects the wrong length
  or any symbol outside the observed alphabet with `422`, not a `500`.

## Architecture: registry-driven training, self-contained serving

```
training/train.py  --logs params/metrics/model-->  MLflow tracking (SQLite)
        |                                                    |
        | encode_sequences()                                 | registers a new
        v                                                    v version of
  app/features.py  <--------- shared by both -----   "splice-junction-classifier"
        ^                                                    |
        |                                       training/promote_model.py
        |                                       aliases the latest version
        |                                       "production", exports it
        |                                                    |
        |                                                    v
  app/main.py  <---loads at startup--- app/model_artifact/{model.joblib,metadata.json}
  (FastAPI)                            (plain scikit-learn pipeline, committed to git)
```

**Why the serving app never talks to MLflow at request time.** MLflow's
Model Registry is genuinely used here — `train.py` registers a real new
version on every run, and `promote_model.py` aliases a specific version
as `production` via the real registry API (`set_registered_model_alias`,
not a stage attribute, which MLflow has deprecated). But the *serving*
container loads a plain joblib-pickled scikit-learn pipeline from disk,
with no MLflow (or pandas) dependency at all — see the `training` extra
in `pyproject.toml`, which the Dockerfile's runtime stage never installs.
This keeps the deployed image small, keeps inference latency independent
of a registry's availability, and makes deployments reproducible: a
given image tag always serves exactly the model version that was baked
into it, not "whatever the registry currently points at." The tradeoff
is explicit: promoting a new model version means rebuilding and
redeploying the image, not just flipping an alias. See `docs/adr/` for
more on this and the FastAPI/Kubernetes choices.

`app/features.py` (not `training/features.py`) holds the one-hot
encoding logic specifically so both sides of that diagram use the exact
same code — training and serving can never silently drift apart on how
a sequence becomes a feature vector.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest   # 90%+ coverage gate; see pyproject.toml
```

Retrain and re-promote the committed model artifact (writes a local
`mlflow.db`/`mlruns/`, both gitignored, and overwrites
`app/model_artifact/`):

```bash
python -m training.train
python -m training.promote_model
```

Run the API directly against the committed artifact:

```bash
uvicorn app.main:app --reload
curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"sequence": "CCAGCTGCATCACAGGAGGCCAGCGAGCAGGTCTGTTCCAAGGGCCTTCGAGCCAGTCTG"}'
```

## Container

```bash
docker build -t genomerse-model-serving .
docker run --rm -p 8000:8000 genomerse-model-serving
```

No `docker-compose.yml` in this service on purpose — see
[`docs/adr/0002-kubernetes-helm-over-docker-compose.md`](../../docs/adr/0002-kubernetes-helm-over-docker-compose.md).
A bare `docker run` is enough for a pre-Kubernetes smoke test.

## Kubernetes / Helm

See [`infra/k8s/README.md`](../../infra/k8s/README.md) and
[`infra/helm/model-serving/`](../../infra/helm/model-serving) for
deploying to a local `kind` cluster.
