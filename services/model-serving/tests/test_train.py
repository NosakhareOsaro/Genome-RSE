from pathlib import Path

import mlflow

from app.features import encode_sequences
from training.data import SEQUENCE_LENGTH, SpliceRecord
from training.train import train_and_register


def _synthetic_records(per_class: int = 8) -> list[SpliceRecord]:
    """A tiny, deterministic dataset -- enough for a stratified split
    across 3 classes without depending on the full cached dataset, so
    this test stays fast and independent of data/splice.data.
    """
    bases = {"EI": "A", "IE": "C", "N": "G"}
    records = []
    for label, base in bases.items():
        for i in range(per_class):
            # Vary one position per instance so sequences aren't identical.
            sequence = list(base * SEQUENCE_LENGTH)
            sequence[i % SEQUENCE_LENGTH] = "T"
            records.append(
                SpliceRecord(label=label, instance_name=f"{label}-{i}", sequence="".join(sequence))
            )
    return records


def test_train_and_register_logs_and_registers_model(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    records = _synthetic_records()

    result = train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name="test-splice-classifier",
        n_estimators=10,
        test_size=0.25,
    )

    assert result.run_id
    assert result.registered_model_name == "test-splice-classifier"
    assert result.model_version
    assert 0.0 <= result.accuracy <= 1.0
    assert 0.0 <= result.macro_f1 <= 1.0

    client = mlflow.MlflowClient(tracking_uri=tracking_uri)
    version = client.get_model_version("test-splice-classifier", result.model_version)
    assert version.run_id == result.run_id

    run = client.get_run(result.run_id)
    assert run.data.params["model_type"] == "RandomForestClassifier"
    assert "accuracy" in run.data.metrics
    assert "macro_f1" in run.data.metrics


def test_train_and_register_creates_loadable_model(tmp_path: Path) -> None:
    tracking_uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    records = _synthetic_records()

    result = train_and_register(
        records,
        tracking_uri=tracking_uri,
        registered_model_name="test-splice-classifier-2",
        n_estimators=10,
    )

    mlflow.set_tracking_uri(tracking_uri)
    loaded = mlflow.sklearn.load_model(f"models:/test-splice-classifier-2/{result.model_version}")

    features = encode_sequences([records[0].sequence])
    predictions = loaded.predict(features)
    assert predictions[0] in {"EI", "IE", "N"}
