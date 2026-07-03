"""Loads the bundled model artifact from disk.

Deliberately has no MLflow dependency: the artifact under
``app/model_artifact/`` (produced by ``training/promote_model.py``) is a
plain scikit-learn pipeline plus a metadata sidecar, so the serving
container never needs to reach a live MLflow Model Registry to answer a
request.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

SERVICE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_DIR = SERVICE_ROOT / "app" / "model_artifact"


@dataclass(frozen=True)
class ModelMetadata:
    registered_model_name: str
    model_version: int
    run_id: str
    alias: str
    accuracy: float
    macro_f1: float
    promoted_at: str


@dataclass(frozen=True)
class ModelBundle:
    model: Any
    metadata: ModelMetadata


def artifact_dir() -> Path:
    configured = os.environ.get("MODEL_ARTIFACT_DIR")
    if not configured:
        return DEFAULT_ARTIFACT_DIR
    path = Path(configured)
    return path if path.is_absolute() else SERVICE_ROOT / path


def load_model_bundle(directory: Path | None = None) -> ModelBundle:
    """Load the model + metadata from ``directory`` (default: ``artifact_dir()``).

    Raises ``FileNotFoundError`` if either file is missing -- there's no
    sensible fallback for a serving process with no model to serve.
    """
    resolved_dir = directory or artifact_dir()
    model_path = resolved_dir / "model.joblib"
    metadata_path = resolved_dir / "metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"no model artifact at {model_path} -- run training/train.py then "
            "training/promote_model.py first"
        )
    if not metadata_path.exists():
        raise FileNotFoundError(f"no model metadata at {metadata_path}")

    model = joblib.load(model_path)
    metadata = ModelMetadata(**json.loads(metadata_path.read_text()))
    return ModelBundle(model=model, metadata=metadata)
