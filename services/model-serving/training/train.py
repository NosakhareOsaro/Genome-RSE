"""Train the demonstration splice-junction classifier and register it in
the MLflow Model Registry.

This is a small, fast, CPU-only classifier meant to demonstrate an MLOps
train -> register -> promote -> serve pipeline -- it is explicitly NOT a
production-grade splice-site predictor (real tools like SpliceAI use deep
CNNs over much larger genomic context). See services/model-serving/README.md.

Usage::

    python -m training.train

Reads MLFLOW_TRACKING_URI (default: a local SQLite file, sqlite:///mlflow.db,
resolved relative to the service root) and MLFLOW_REGISTERED_MODEL_NAME
(default: "splice-junction-classifier") from the environment. A SQLite-backed
tracking store -- rather than the plain file-based store -- is required
because the MLflow Model Registry needs a SQLAlchemy-compatible backend.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.features import encode_sequences
from training.data import SpliceRecord, load_splice_records

SERVICE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTERED_MODEL_NAME = "splice-junction-classifier"
RANDOM_STATE = 42


@dataclass(frozen=True)
class TrainingResult:
    run_id: str
    registered_model_name: str
    model_version: str
    accuracy: float
    macro_f1: float


def default_tracking_uri() -> str:
    return f"sqlite:///{SERVICE_ROOT / 'mlflow.db'}"


def _build_pipeline(n_estimators: int, max_depth: int | None) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            )
        ]
    )


def train_and_register(
    records: list[SpliceRecord],
    *,
    tracking_uri: str,
    registered_model_name: str = DEFAULT_REGISTERED_MODEL_NAME,
    n_estimators: int = 50,
    max_depth: int | None = 12,
    test_size: float = 0.2,
) -> TrainingResult:
    """Train on ``records``, log to MLflow, and register a new model version.

    Split into train/test, fits a RandomForest over one-hot encoded
    sequences, logs params/metrics/model to MLflow tracking, and registers
    the logged model as a new version of ``registered_model_name`` in the
    MLflow Model Registry (creating the registered model if it doesn't
    exist yet).
    """
    mlflow.set_tracking_uri(tracking_uri)

    sequences = [record.sequence for record in records]
    labels = [record.label for record in records]
    features = encode_sequences(sequences)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    pipeline = _build_pipeline(n_estimators=n_estimators, max_depth=max_depth)

    with mlflow.start_run() as run:
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        accuracy = float(accuracy_score(y_test, predictions))
        macro_f1 = float(f1_score(y_test, predictions, average="macro"))

        mlflow.log_params(
            {
                "model_type": "RandomForestClassifier",
                "n_estimators": n_estimators,
                "max_depth": max_depth,
                "test_size": test_size,
                "random_state": RANDOM_STATE,
                "n_train_samples": len(x_train),
                "n_test_samples": len(x_test),
            }
        )
        mlflow.log_metrics({"accuracy": accuracy, "macro_f1": macro_f1})

        model_info = mlflow.sklearn.log_model(
            pipeline,
            name="model",
            registered_model_name=registered_model_name,
        )

    return TrainingResult(
        run_id=run.info.run_id,
        registered_model_name=registered_model_name,
        model_version=model_info.registered_model_version,
        accuracy=accuracy,
        macro_f1=macro_f1,
    )


def main() -> None:
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", default_tracking_uri())
    registered_model_name = os.environ.get(
        "MLFLOW_REGISTERED_MODEL_NAME", DEFAULT_REGISTERED_MODEL_NAME
    )
    records = load_splice_records()
    result = train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name=registered_model_name,
    )
    print(
        f"Registered {result.registered_model_name} version "
        f"{result.model_version} (run {result.run_id}): "
        f"accuracy={result.accuracy:.4f} macro_f1={result.macro_f1:.4f}"
    )


if __name__ == "__main__":
    main()
