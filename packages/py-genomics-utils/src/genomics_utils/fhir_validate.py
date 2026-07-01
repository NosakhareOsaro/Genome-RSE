"""Minimal FHIR R4 resource validator.

**Scope note (read this before relying on this module):** this validator
only checks that a JSON document has the *shape* of a small, hand-picked
subset of the FHIR R4 ``Patient`` and ``Observation`` resource types:
that the fields this module models are present when the FHIR spec
requires them (e.g. ``Observation.status`` and ``Observation.code``) and
have the correct basic type/enum values. Any field not modeled here
(``identifier``, ``telecom``, ``address``, ``component``, extensions,
etc.) is passed through without validation.

This is **not** full FHIR conformance validation:

- No terminology binding checks (e.g. it does not verify that a
  ``system``/``code`` pair in a ``Coding`` actually exists in that code
  system).
- No StructureDefinition/profile validation.
- No referential integrity checks (e.g. it does not verify that
  ``Observation.subject.reference`` points to a resource that exists).

For conformance-grade validation, use the official
`HL7 FHIR validator <https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Validator>`_.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class Coding(BaseModel):
    """A minimal subset of the FHIR ``Coding`` data type."""

    model_config = ConfigDict(extra="ignore")

    system: str | None = None
    code: str | None = None
    display: str | None = None


class CodeableConcept(BaseModel):
    """A minimal subset of the FHIR ``CodeableConcept`` data type."""

    model_config = ConfigDict(extra="ignore")

    coding: list[Coding] | None = None
    text: str | None = None


class Reference(BaseModel):
    """A minimal subset of the FHIR ``Reference`` data type."""

    model_config = ConfigDict(extra="ignore")

    reference: str | None = None
    display: str | None = None


class HumanName(BaseModel):
    """A minimal subset of the FHIR ``HumanName`` data type."""

    model_config = ConfigDict(extra="ignore")

    use: str | None = None
    family: str | None = None
    given: list[str] | None = None


class ObservationStatus(str, Enum):
    """The FHIR R4 ``Observation.status`` required value set."""

    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class PatientResource(BaseModel):
    """Minimal structural model of a FHIR R4 ``Patient`` resource.

    Per the FHIR R4 spec, ``Patient`` has no required elements beyond
    ``resourceType``; the fields below are validated for shape/type
    *if present*, not required.
    """

    model_config = ConfigDict(extra="ignore")

    resourceType: Literal["Patient"]
    id: str | None = None
    active: bool | None = None
    name: list[HumanName] | None = None
    gender: Literal["male", "female", "other", "unknown"] | None = None
    birthDate: date | None = None


class ObservationResource(BaseModel):
    """Minimal structural model of a FHIR R4 ``Observation`` resource.

    ``status`` and ``code`` are genuinely required by the FHIR R4 spec
    (cardinality ``1..1``) and are enforced as required here too.
    """

    model_config = ConfigDict(extra="ignore")

    resourceType: Literal["Observation"]
    id: str | None = None
    status: ObservationStatus
    code: CodeableConcept
    subject: Reference | None = None


_SUPPORTED_RESOURCE_MODELS: dict[str, type[BaseModel]] = {
    "Patient": PatientResource,
    "Observation": ObservationResource,
}


@dataclass
class ValidationResult:
    """The outcome of validating one resource against its minimal model."""

    valid: bool
    resource_type: str | None
    errors: list[str] = field(default_factory=list)


def validate_resource(data: dict) -> ValidationResult:
    """Structurally validate a parsed FHIR resource dict.

    See the module docstring for exactly what is and is not checked.
    """
    resource_type = data.get("resourceType") if isinstance(data, dict) else None
    model = _SUPPORTED_RESOURCE_MODELS.get(resource_type) if resource_type else None

    if model is None:
        supported = ", ".join(sorted(_SUPPORTED_RESOURCE_MODELS))
        return ValidationResult(
            valid=False,
            resource_type=resource_type,
            errors=[
                f"Unsupported or missing resourceType {resource_type!r}; "
                f"this validator only supports: {supported}"
            ],
        )

    try:
        model.model_validate(data)
    except ValidationError as exc:
        errors = [f"{'.'.join(str(p) for p in err['loc']) or '(root)'}: {err['msg']}" for err in exc.errors()]
        return ValidationResult(valid=False, resource_type=resource_type, errors=errors)

    return ValidationResult(valid=True, resource_type=resource_type, errors=[])


def validate_resource_file(path: str | Path) -> ValidationResult:
    """Load a JSON file and validate it with :func:`validate_resource`."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_resource(data)
