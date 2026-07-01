from __future__ import annotations

from httpx import AsyncClient


async def test_create_resource(client: AsyncClient, read_write_headers: dict[str, str]):
    response = await client.post(
        "/MolecularSequence",
        json={"coordinateSystem": 0, "type": "dna", "patient": {"reference": "Patient/abc"}},
        headers=read_write_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["resourceType"] == "MolecularSequence"
    assert body["coordinateSystem"] == 0
    assert body["type"] == "dna"
    assert body["patient"]["reference"] == "Patient/abc"
    assert "id" in body
    assert "display" not in body["patient"]  # null fields excluded


async def test_create_resource_missing_required_field(
    client: AsyncClient, read_write_headers: dict[str, str]
):
    response = await client.post(
        "/MolecularSequence", json={"patient": {"reference": "Patient/abc"}}, headers=read_write_headers
    )
    assert response.status_code == 422


async def test_create_resource_requires_write_scope(
    client: AsyncClient, read_only_headers: dict[str, str]
):
    response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_only_headers
    )
    assert response.status_code == 403


async def test_read_resource(client: AsyncClient, read_write_headers: dict[str, str]):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 1}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    response = await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert response.status_code == 200
    assert response.json()["id"] == resource_id


async def test_read_resource_not_found(client: AsyncClient, read_only_headers: dict[str, str]):
    response = await client.get("/MolecularSequence/nonexistent-id", headers=read_only_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "MolecularSequence not found"


async def test_read_resource_requires_read_scope(
    client: AsyncClient, write_only_headers: dict[str, str]
):
    response = await client.get("/MolecularSequence/some-id", headers=write_only_headers)
    assert response.status_code == 403


async def test_search_resources_by_patient(client: AsyncClient, read_write_headers: dict[str, str]):
    await client.post(
        "/MolecularSequence",
        json={"coordinateSystem": 0, "patient": {"reference": "Patient/abc"}},
        headers=read_write_headers,
    )
    await client.post(
        "/MolecularSequence",
        json={"coordinateSystem": 0, "patient": {"reference": "Patient/xyz"}},
        headers=read_write_headers,
    )

    response = await client.get(
        "/MolecularSequence", params={"patient": "Patient/abc"}, headers=read_write_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["resourceType"] == "Bundle"
    assert body["type"] == "searchset"
    assert body["total"] == 1
    assert body["entry"][0]["resource"]["patient"]["reference"] == "Patient/abc"


async def test_search_resources_without_filter_returns_all(
    client: AsyncClient, read_write_headers: dict[str, str]
):
    for _ in range(3):
        await client.post(
            "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
        )

    response = await client.get("/MolecularSequence", headers=read_write_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 3


async def test_search_resources_count_limit(client: AsyncClient, read_write_headers: dict[str, str]):
    for _ in range(3):
        await client.post(
            "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
        )

    response = await client.get(
        "/MolecularSequence", params={"_count": 2}, headers=read_write_headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 2


async def test_search_resources_count_out_of_range(
    client: AsyncClient, read_write_headers: dict[str, str]
):
    response = await client.get(
        "/MolecularSequence", params={"_count": 0}, headers=read_write_headers
    )
    assert response.status_code == 422


async def test_update_resource(client: AsyncClient, read_write_headers: dict[str, str]):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    response = await client.put(
        f"/MolecularSequence/{resource_id}",
        json={"coordinateSystem": 5, "patient": {"reference": "Patient/new"}},
        headers=read_write_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["coordinateSystem"] == 5
    assert body["patient"]["reference"] == "Patient/new"
    assert body["id"] == resource_id


async def test_update_resource_not_found(client: AsyncClient, read_write_headers: dict[str, str]):
    response = await client.put(
        "/MolecularSequence/nonexistent-id",
        json={"coordinateSystem": 0},
        headers=read_write_headers,
    )
    assert response.status_code == 404


async def test_update_resource_requires_write_scope(
    client: AsyncClient, read_only_headers: dict[str, str]
):
    response = await client.put(
        "/MolecularSequence/some-id", json={"coordinateSystem": 0}, headers=read_only_headers
    )
    assert response.status_code == 403


async def test_delete_resource(client: AsyncClient, read_write_headers: dict[str, str]):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/MolecularSequence/{resource_id}", headers=read_write_headers
    )
    assert delete_response.status_code == 204

    read_response = await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert read_response.status_code == 404


async def test_delete_resource_not_found(client: AsyncClient, read_write_headers: dict[str, str]):
    response = await client.delete("/MolecularSequence/nonexistent-id", headers=read_write_headers)
    assert response.status_code == 404


async def test_delete_resource_requires_write_scope(
    client: AsyncClient, read_only_headers: dict[str, str]
):
    response = await client.delete("/MolecularSequence/some-id", headers=read_only_headers)
    assert response.status_code == 403
