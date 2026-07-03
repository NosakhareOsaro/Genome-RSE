import json
from pathlib import Path

import joblib
import pytest

from app.features import encode_sequences
from tests.test_train import _synthetic_records
from training.promote_model import PRODUCTION_ALIAS, promote_latest_to_production
from training.train import train_and_register


def test_promote_latest_to_production(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    artifact_dir = tmp_path / "model_artifact"
    records = _synthetic_records()

    trained = train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name="promote-test-model",
        n_estimators=10,
    )

    result = promote_latest_to_production(
        tracking_uri=tracking_uri,
        registered_model_name="promote-test-model",
        artifact_dir=artifact_dir,
    )

    assert result.model_version == trained.model_version
    assert result.run_id == trained.run_id

    model_path = artifact_dir / "model.joblib"
    metadata_path = artifact_dir / "metadata.json"
    assert model_path.exists()
    assert metadata_path.exists()

    metadata = json.loads(metadata_path.read_text())
    assert metadata["registered_model_name"] == "promote-test-model"
    assert metadata["model_version"] == trained.model_version
    assert metadata["alias"] == PRODUCTION_ALIAS

    loaded_model = joblib.load(model_path)
    features = encode_sequences([records[0].sequence])
    prediction = loaded_model.predict(features)
    assert prediction[0] in {"EI", "IE", "N"}


def test_promote_latest_to_production_promotes_newest_version(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    artifact_dir = tmp_path / "model_artifact"
    records = _synthetic_records()

    train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name="promote-test-model-2",
        n_estimators=10,
    )
    second = train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name="promote-test-model-2",
        n_estimators=10,
    )

    result = promote_latest_to_production(
        tracking_uri=tracking_uri,
        registered_model_name="promote-test-model-2",
        artifact_dir=artifact_dir,
    )

    assert result.model_version == second.model_version


def test_promote_raises_if_no_versions_registered(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    with pytest.raises(ValueError, match="no registered versions found"):
        promote_latest_to_production(
            tracking_uri=tracking_uri,
            registered_model_name="never-registered-model",
            artifact_dir=tmp_path / "model_artifact",
        )
