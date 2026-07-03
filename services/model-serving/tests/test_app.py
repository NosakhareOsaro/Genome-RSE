import json

import pytest
from fastapi.testclient import TestClient

from app.main import app

# A real EI-labeled instance from data/splice.data (ATRINS-DONOR-521).
SAMPLE_SEQUENCE = "CCAGCTGCATCACAGGAGGCCAGCGAGCAGGTCTGTTCCAAGGGCCTTCGAGCCAGTCTG"


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_model_info_matches_committed_metadata(client: TestClient) -> None:
    from app.model_loader import artifact_dir

    response = client.get("/model-info")
    assert response.status_code == 200
    body = response.json()

    on_disk = json.loads((artifact_dir() / "metadata.json").read_text())
    assert body["registered_model_name"] == on_disk["registered_model_name"]
    assert body["model_version"] == on_disk["model_version"]
    assert body["run_id"] == on_disk["run_id"]
    assert body["alias"] == "production"


def test_predict_returns_a_known_class_and_probabilities(client: TestClient) -> None:
    response = client.post("/predict", json={"sequence": SAMPLE_SEQUENCE})
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_class"] in {"EI", "IE", "N"}
    assert set(body["probabilities"].keys()) == {"EI", "IE", "N"}
    assert abs(sum(body["probabilities"].values()) - 1.0) < 1e-6


def test_predict_is_case_insensitive(client: TestClient) -> None:
    response = client.post("/predict", json={"sequence": SAMPLE_SEQUENCE.lower()})
    assert response.status_code == 200


def test_predict_rejects_wrong_length(client: TestClient) -> None:
    response = client.post("/predict", json={"sequence": "ACGT"})
    assert response.status_code == 422


def test_predict_rejects_invalid_symbol(client: TestClient) -> None:
    sequence = "X" + SAMPLE_SEQUENCE[1:]
    response = client.post("/predict", json={"sequence": sequence})
    assert response.status_code == 422


def test_predict_missing_field(client: TestClient) -> None:
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_model_not_loaded_raises_503() -> None:
    from fastapi import HTTPException

    from app.main import _get_bundle, _state

    _state.pop("bundle", None)
    with pytest.raises(HTTPException) as excinfo:
        _get_bundle()
    assert excinfo.value.status_code == 503
