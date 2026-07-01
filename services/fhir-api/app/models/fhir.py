"""Minimal FHIR R4 ``MolecularSequence`` resource model.

**Scope note:** this models a small, hand-picked subset of the FHIR R4
``MolecularSequence`` resource -- enough to demonstrate a genuine FHIR
RESTful API (create/read/search/update/delete, returned as spec-shaped
JSON) without implementing every element FHIR defines (e.g. ``variant``,
``quality``, ``repository`` are not modeled). Unmodeled fields are
ignored on input rather than rejected, matching the same
structural-subset approach used by
``packages/py-genomics-utils``'s FHIR validator in Phase 1.

Field names are exposed over the wire in FHIR's camelCase JSON
convention (via pydantic aliases); Python code uses snake_case
attributes.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Coding(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    system: str | None = None
    code: str | None = None
    display: str | None = None


class CodeableConcept(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    coding: list[Coding] | None = None
    text: str | None = None


class ReferenceModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    reference: str | None = None
    display: str | None = None


class ReferenceSeq(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chromosome: CodeableConcept | None = None
    genome_build: str | None = Field(default=None, alias="genomeBuild")
    window_start: int | None = Field(default=None, alias="windowStart")
    window_end: int | None = Field(default=None, alias="windowEnd")


class MolecularSequenceType(str, Enum):
    AA = "aa"
    DNA = "dna"
    RNA = "rna"


class MolecularSequenceBase(BaseModel):
    """Fields a client supplies when creating or replacing a resource."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    type: MolecularSequenceType | None = None
    # `coordinateSystem` is cardinality 1..1 (required) in the real FHIR R4 spec.
    coordinate_system: int = Field(alias="coordinateSystem")
    patient: ReferenceModel | None = None
    reference_seq: ReferenceSeq | None = Field(default=None, alias="referenceSeq")
    read_coverage: int | None = Field(default=None, alias="readCoverage")


class MolecularSequenceResource(MolecularSequenceBase):
    """The full resource as returned by the API."""

    resource_type: Literal["MolecularSequence"] = Field(
        default="MolecularSequence", alias="resourceType"
    )
    id: str
