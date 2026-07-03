from pathlib import Path

import pytest

from app.model_loader import DEFAULT_ARTIFACT_DIR, artifact_dir, load_model_bundle


def test_artifact_dir_defaults_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_ARTIFACT_DIR", raising=False)
    assert artifact_dir() == DEFAULT_ARTIFACT_DIR


def test_artifact_dir_honors_relative_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MODEL_ARTIFACT_DIR", "some/relative/dir")
    resolved = artifact_dir()
    assert resolved.is_absolute()
    assert resolved.name == "dir"


def test_artifact_dir_honors_absolute_env_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("MODEL_ARTIFACT_DIR", str(tmp_path))
    assert artifact_dir() == tmp_path


def test_load_model_bundle_from_real_committed_artifact() -> None:
    bundle = load_model_bundle()
    assert bundle.metadata.registered_model_name == "splice-junction-classifier"
    assert bundle.metadata.alias == "production"


def test_load_model_bundle_missing_model_raises(tmp_path: Path) -> None:
    (tmp_path / "metadata.json").write_text("{}")
    with pytest.raises(FileNotFoundError, match="no model artifact"):
        load_model_bundle(tmp_path)


def test_load_model_bundle_missing_metadata_raises(tmp_path: Path) -> None:
    (tmp_path / "model.joblib").write_bytes(b"not a real pickle, just needs to exist")
    with pytest.raises(FileNotFoundError, match="no model metadata"):
        load_model_bundle(tmp_path)
