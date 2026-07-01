"""FHIR RESTful interactions for the MolecularSequence resource type.

Implements create, read, search, update, and delete -- the standard
FHIR "instance" and "type" level interactions -- backed by app.crud.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.auth.security import require_scope
from app.cache import get_cached_resource, get_redis, invalidate_cached_resource, set_cached_resource
from app.config import get_settings
from app.db import get_db_session
from app.models.fhir import Bundle, BundleEntry, MolecularSequenceBase, MolecularSequenceResource

READ_SCOPE = "system/MolecularSequence.read"
WRITE_SCOPE = "system/MolecularSequence.write"

router = APIRouter(prefix="/MolecularSequence", tags=["MolecularSequence"])

NOT_FOUND_DETAIL = "MolecularSequence not found"


@router.post(
    "",
    response_model=MolecularSequenceResource,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_resource(
    body: MolecularSequenceBase,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _token: Annotated[dict[str, Any], Depends(require_scope(WRITE_SCOPE))],
) -> MolecularSequenceResource:
    resource_dict = body.model_dump(by_alias=True, exclude_none=True)
    row = await crud.create_molecular_sequence(session, resource_dict)
    return MolecularSequenceResource.model_validate(row.resource)


@router.get(
    "/{resource_id}", response_model=MolecularSequenceResource, response_model_exclude_none=True
)
async def read_resource(
    resource_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    _token: Annotated[dict[str, Any], Depends(require_scope(READ_SCOPE))],
) -> MolecularSequenceResource:
    cached = await get_cached_resource(redis, resource_id)
    if cached is not None:
        return MolecularSequenceResource.model_validate(cached)

    row = await crud.get_molecular_sequence(session, resource_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)

    await set_cached_resource(redis, resource_id, row.resource, get_settings().cache_ttl_seconds)
    return MolecularSequenceResource.model_validate(row.resource)


@router.get("", response_model=Bundle, response_model_exclude_none=True)
async def search_resources(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _token: Annotated[dict[str, Any], Depends(require_scope(READ_SCOPE))],
    patient: str | None = Query(default=None, description="Patient reference, e.g. Patient/123"),
    count: int = Query(default=20, ge=1, le=100, alias="_count"),
) -> Bundle:
    rows = await crud.search_molecular_sequences(session, patient_reference=patient, count=count)
    entries = [
        BundleEntry(resource=MolecularSequenceResource.model_validate(row.resource)) for row in rows
    ]
    return Bundle(total=len(entries), entry=entries)


@router.put(
    "/{resource_id}", response_model=MolecularSequenceResource, response_model_exclude_none=True
)
async def update_resource(
    resource_id: str,
    body: MolecularSequenceBase,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    _token: Annotated[dict[str, Any], Depends(require_scope(WRITE_SCOPE))],
) -> MolecularSequenceResource:
    resource_dict = body.model_dump(by_alias=True, exclude_none=True)
    row = await crud.update_molecular_sequence(session, resource_id, resource_dict)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    await invalidate_cached_resource(redis, resource_id)
    return MolecularSequenceResource.model_validate(row.resource)


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    _token: Annotated[dict[str, Any], Depends(require_scope(WRITE_SCOPE))],
) -> Response:
    deleted = await crud.delete_molecular_sequence(session, resource_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    await invalidate_cached_resource(redis, resource_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
