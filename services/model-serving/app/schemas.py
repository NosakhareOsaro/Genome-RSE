"""Pydantic request/response models for the serving API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.features import ALPHABET, SEQUENCE_LENGTH


class PredictRequest(BaseModel):
    sequence: str = Field(
        ...,
        description=(
            f"A {SEQUENCE_LENGTH}-nucleotide DNA window, alphabet "
            f"{ALPHABET} (case-insensitive)."
        ),
        examples=["CCAGCTGCATCACAGGAGGCCAGCGAGCAGGTCTGTTCCAAGGGCCTTCGAGCCAGTCTG"],
    )

    @field_validator("sequence")
    @classmethod
    def _validate_sequence(cls, value: str) -> str:
        value = value.upper()
        if len(value) != SEQUENCE_LENGTH:
            raise ValueError(f"sequence must be exactly {SEQUENCE_LENGTH} nucleotides long")
        invalid = sorted(set(value) - set(ALPHABET))
        if invalid:
            raise ValueError(f"sequence contains symbols outside {ALPHABET}: {invalid}")
        return value


class PredictResponse(BaseModel):
    predicted_class: str = Field(
        ..., description="One of EI (intron->exon), IE (exon->intron), or N (neither)."
    )
    probabilities: dict[str, float] = Field(
        ..., description="Class probabilities as reported by the underlying classifier."
    )


class ModelInfoResponse(BaseModel):
    registered_model_name: str
    model_version: int
    run_id: str
    alias: str
    accuracy: float
    macro_f1: float
    promoted_at: str


class HealthResponse(BaseModel):
    status: str = "ok"
