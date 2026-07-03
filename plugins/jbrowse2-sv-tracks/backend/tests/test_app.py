import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_svs_returns_records_for_valid_region(client):
    response = client.get("/api/svs?refName=ctgA&start=0&end=50001")
    assert response.status_code == 200
    body = response.get_json()
    assert {r["id"] for r in body} == {"sv1_del", "sv2_dup", "sv3_inv", "sv4_bnd_1"}


def test_svs_filters_by_region(client):
    response = client.get("/api/svs?refName=ctgA&start=15000&end=20000")
    assert response.status_code == 200
    assert {r["id"] for r in response.get_json()} == {"sv2_dup"}


def test_svs_unknown_contig_returns_empty_list(client):
    response = client.get("/api/svs?refName=does-not-exist&start=0&end=100")
    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.parametrize(
    "query",
    [
        "start=0&end=100",  # missing refName
        "refName=ctgA&end=100",  # missing start
        "refName=ctgA&start=0",  # missing end
    ],
)
def test_svs_missing_required_param_returns_400(client, query):
    response = client.get(f"/api/svs?{query}")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_svs_negative_start_returns_400(client):
    response = client.get("/api/svs?refName=ctgA&start=-5&end=100")
    assert response.status_code == 400


def test_svs_end_before_start_returns_400(client):
    response = client.get("/api/svs?refName=ctgA&start=100&end=50")
    assert response.status_code == 400


def test_cors_header_present(client):
    response = client.get("/api/health")
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
