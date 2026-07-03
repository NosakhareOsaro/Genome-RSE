"""Promote the latest registered model version to "production" and export
it as a self-contained artifact for the serving container.

This is the seam between "MLflow owns versioning/lineage" and "the
serving image is a self-contained, reproducible build artifact": the
FastAPI app (app/model_loader.py) never talks to MLflow at request time,
it just loads whatever this script last exported to app/model_artifact/.
That's a deliberate choice, not an oversight -- see docs/adr/ for the
rationale once written, and the service README in the meantime.

Usage::

    python -m training.promote_model
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import joblib
import mlflow
from mlflow import MlflowClient

from training.train import DEFAULT_REGISTERED_MODEL_NAME, SERVICE_ROOT, default_tracking_uri

DEFAULT_ARTIFACT_DIR = SERVICE_ROOT / "app" / "model_artifact"
PRODUCTION_ALIAS = "production"


@dataclass(frozen=True)
class PromotionResult:
    registered_model_name: str
    model_version: str
    run_id: str
    accuracy: float
    macro_f1: float


def _latest_version(client: MlflowClient, registered_model_name: str):
    versions = client.search_model_versions(
        filter_string=f"name='{registered_model_name}'",
        order_by=["version_number DESC"],
        max_results=1,
    )
    if not versions:
        raise ValueError(
            f"no registered versions found for {registered_model_name!r} -- "
            "run training/train.py first"
        )
    return versions[0]


def promote_latest_to_production(
    *,
    tracking_uri: str,
    registered_model_name: str = DEFAULT_REGISTERED_MODEL_NAME,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
) -> PromotionResult:
    """Alias the latest registered model version as "production" and
    export it (plain scikit-learn pipeline + metadata) to ``artifact_dir``.
    """
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient(tracking_uri=tracking_uri)

    latest = _latest_version(client, registered_model_name)
    client.set_registered_model_alias(registered_model_name, PRODUCTION_ALIAS, latest.version)

    run = client.get_run(latest.run_id)
    model = mlflow.sklearn.load_model(f"models:/{registered_model_name}@{PRODUCTION_ALIAS}")

    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "model.joblib")

    accuracy = float(run.data.metrics["accuracy"])
    macro_f1 = float(run.data.metrics["macro_f1"])
    metadata = {
        "registered_model_name": registered_model_name,
        "model_version": latest.version,
        "run_id": latest.run_id,
        "alias": PRODUCTION_ALIAS,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "promoted_at": datetime.now(UTC).isoformat(),
    }
    (artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    return PromotionResult(
        registered_model_name=registered_model_name,
        model_version=latest.version,
        run_id=latest.run_id,
        accuracy=accuracy,
        macro_f1=macro_f1,
    )


def main() -> None:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", default_tracking_uri())
    registered_model_name = os.environ.get(
        "MLFLOW_REGISTERED_MODEL_NAME", DEFAULT_REGISTERED_MODEL_NAME
    )
    result = promote_latest_to_production(
        tracking_uri=tracking_uri,
        registered_model_name=registered_model_name,
    )
    print(
        f"Promoted {result.registered_model_name} version {result.model_version} "
        f"(run {result.run_id}) to '{PRODUCTION_ALIAS}': "
        f"accuracy={result.accuracy:.4f} macro_f1={result.macro_f1:.4f}"
    )


if __name__ == "__main__":
    main()
