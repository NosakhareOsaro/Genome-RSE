"""SQLAlchemy ORM model backing the FHIR MolecularSequence API.

Deliberate storage design: a few columns that need to be searched or
indexed (``patient_reference``, ``coordinate_system``) live as real
columns, while the full FHIR resource is stored verbatim as JSON in
``resource``. Reads reconstruct the exact resource that was written
(byte-for-byte field fidelity) while still letting the DB index and
filter on the handful of fields the search API supports. This trades
some write-time duplication (indexed fields also live inside the JSON
blob) for read-path simplicity and forward compatibility: adding a new
FHIR field to the resource never requires a migration, only adding a
new *search* field would.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MolecularSequenceORM(Base):
    __tablename__ = "molecular_sequences"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_reference: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    coordinate_system: Mapped[int] = mapped_column(Integer, nullable=False)
    resource: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
