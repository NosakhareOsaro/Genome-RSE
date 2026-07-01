"""Async CRUD operations for MolecularSequence resources.

Functions here take/return plain dicts and ORM rows -- FHIR
serialization (aliasing, response shaping) is the router's job, not
this module's.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import MolecularSequenceORM


def _patient_reference(resource: dict[str, Any]) -> str | None:
    patient = resource.get("patient") or {}
    return patient.get("reference")


async def create_molecular_sequence(
    session: AsyncSession, resource: dict[str, Any]
) -> MolecularSequenceORM:
    resource_id = str(uuid.uuid4())
    stored_resource = {**resource, "resourceType": "MolecularSequence", "id": resource_id}
    row = MolecularSequenceORM(
        id=resource_id,
        patient_reference=_patient_reference(resource),
        coordinate_system=resource["coordinateSystem"],
        resource=stored_resource,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def get_molecular_sequence(
    session: AsyncSession, resource_id: str
) -> MolecularSequenceORM | None:
    return await session.get(MolecularSequenceORM, resource_id)


async def search_molecular_sequences(
    session: AsyncSession,
    patient_reference: str | None = None,
    count: int = 20,
) -> list[MolecularSequenceORM]:
    stmt = select(MolecularSequenceORM)
    if patient_reference is not None:
        stmt = stmt.where(MolecularSequenceORM.patient_reference == patient_reference)
    stmt = stmt.order_by(MolecularSequenceORM.created_at).limit(count)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_molecular_sequence(
    session: AsyncSession, resource_id: str, resource: dict[str, Any]
) -> MolecularSequenceORM | None:
    row = await session.get(MolecularSequenceORM, resource_id)
    if row is None:
        return None
    row.patient_reference = _patient_reference(resource)
    row.coordinate_system = resource["coordinateSystem"]
    row.resource = {**resource, "resourceType": "MolecularSequence", "id": resource_id}
    await session.commit()
    await session.refresh(row)
    return row


async def delete_molecular_sequence(session: AsyncSession, resource_id: str) -> bool:
    row = await session.get(MolecularSequenceORM, resource_id)
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True
