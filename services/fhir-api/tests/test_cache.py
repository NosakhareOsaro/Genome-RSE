from __future__ import annotations

import json

from httpx import AsyncClient
from redis.asyncio import Redis

from app.cache import get_cached_resource


async def test_read_populates_cache(
    client: AsyncClient, read_write_headers: dict[str, str], fake_redis: Redis
):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    assert await get_cached_resource(fake_redis, resource_id) is None

    await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)

    cached = await get_cached_resource(fake_redis, resource_id)
    assert cached is not None
    assert cached["id"] == resource_id


async def test_cache_serves_stale_data_until_invalidated(
    client: AsyncClient, read_write_headers: dict[str, str], fake_redis: Redis
):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    # Populate the cache.
    first_read = await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert first_read.json()["coordinateSystem"] == 0

    # Poison the cache directly to prove the read path is actually using it.
    poisoned = {**first_read.json(), "coordinateSystem": 999}
    await fake_redis.set(f"molseq:{resource_id}", json.dumps(poisoned), ex=60)

    second_read = await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert second_read.json()["coordinateSystem"] == 999


async def test_cache_invalidated_on_update(
    client: AsyncClient, read_write_headers: dict[str, str], fake_redis: Redis
):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert await get_cached_resource(fake_redis, resource_id) is not None

    await client.put(
        f"/MolecularSequence/{resource_id}",
        json={"coordinateSystem": 7},
        headers=read_write_headers,
    )
    assert await get_cached_resource(fake_redis, resource_id) is None

    fresh_read = await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert fresh_read.json()["coordinateSystem"] == 7


async def test_cache_invalidated_on_delete(
    client: AsyncClient, read_write_headers: dict[str, str], fake_redis: Redis
):
    create_response = await client.post(
        "/MolecularSequence", json={"coordinateSystem": 0}, headers=read_write_headers
    )
    resource_id = create_response.json()["id"]

    await client.get(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert await get_cached_resource(fake_redis, resource_id) is not None

    await client.delete(f"/MolecularSequence/{resource_id}", headers=read_write_headers)
    assert await get_cached_resource(fake_redis, resource_id) is None
