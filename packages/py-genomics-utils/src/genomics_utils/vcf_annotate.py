"""Minimal VCF annotation helper.

This module parses a small subset of the VCF 4.x text format (enough to
read ``CHROM``/``POS``/``ID``/``REF``/``ALT``/``QUAL``/``FILTER``/``INFO``
columns), classifies each variant record by type, and computes simple
transition/transversion statistics.

It is intentionally lightweight: it does not consult any external
annotation database (e.g. dbSNP, ClinVar, VEP/SnpEff consequence
prediction). It exists to demonstrate a small, well-tested,
dependency-free VCF processing utility, not to replace a production
annotation pipeline.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TextIO

PURINES = frozenset("AG")
PYRIMIDINES = frozenset("CT")

VariantType = str  # one of "SNP", "INS", "DEL", "MNV"


@dataclass(frozen=True)
class VariantRecord:
    """A single parsed VCF data line."""

    chrom: str
    pos: int
    id: str
    ref: str
    alt: str
    qual: str
    filter: str
    info: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class VariantAnnotation:
    """A :class:`VariantRecord` plus derived annotation fields."""

    record: VariantRecord
    variant_type: VariantType
    is_transition: bool | None
    """``True``/``False`` for SNPs, ``None`` for non-SNP variant types."""


@dataclass
class AnnotationSummary:
    """Aggregate counts produced by :func:`annotate_vcf`."""

    total: int = 0
    snp: int = 0
    insertion: int = 0
    deletion: int = 0
    mnv: int = 0
    transitions: int = 0
    transversions: int = 0

    @property
    def ts_tv_ratio(self) -> float | None:
        """Transition/transversion ratio, or ``None`` if no transversions were seen."""
        if self.transversions == 0:
            return None
        return self.transitions / self.transversions

    def as_dict(self) -> dict:
        d = asdict(self)
        d["ts_tv_ratio"] = self.ts_tv_ratio
        return d


def _parse_info(raw_info: str) -> dict[str, str]:
    """Parse a VCF ``INFO`` field into a dict.

    Flag-only entries (no ``=``) are stored with an empty string value.
    """
    info: dict[str, str] = {}
    if raw_info in ("", "."):
        return info
    for entry in raw_info.split(";"):
        if "=" in entry:
            key, _, value = entry.partition("=")
            info[key] = value
        else:
            info[entry] = ""
    return info


def parse_vcf(source: str | Path | TextIO) -> Iterator[VariantRecord]:
    """Parse a VCF file (or open text stream), yielding one record per data line.

    Header lines (starting with ``#``) are skipped. Only single-allele
    ``ALT`` values are supported: a data line with a comma-separated
    multi-allelic ``ALT`` raises :class:`ValueError`.
    """
    if isinstance(source, (str, Path)):
        with open(source, encoding="utf-8") as handle:
            yield from parse_vcf(handle)
        return

    for line in source:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 7:
            raise ValueError(f"Malformed VCF line (expected >=7 tab-separated fields): {line!r}")
        chrom, pos, vid, ref, alt, qual, vfilter = fields[:7]
        if "," in alt:
            raise ValueError(f"Multi-allelic ALT is not supported by this helper: {line!r}")
        raw_info = fields[7] if len(fields) > 7 else ""
        yield VariantRecord(
            chrom=chrom,
            pos=int(pos),
            id=vid,
            ref=ref,
            alt=alt,
            qual=qual,
            filter=vfilter,
            info=_parse_info(raw_info),
        )


def classify_variant(ref: str, alt: str) -> VariantType:
    """Classify a single-allele REF/ALT pair as SNP, INS, DEL, or MNV."""
    if len(ref) == 1 and len(alt) == 1:
        return "SNP"
    if len(ref) < len(alt) and alt.startswith(ref):
        return "INS"
    if len(ref) > len(alt) and ref.startswith(alt):
        return "DEL"
    return "MNV"


def is_transition(ref: str, alt: str) -> bool:
    """Return ``True`` if a single-nucleotide substitution is a transition.

    Only meaningful for SNPs (single-base REF and ALT); callers are
    responsible for checking :func:`classify_variant` first.
    """
    if ref in PURINES and alt in PURINES:
        return True
    if ref in PYRIMIDINES and alt in PYRIMIDINES:
        return True
    return False


def annotate_variants(records: Iterable[VariantRecord]) -> Iterator[VariantAnnotation]:
    """Annotate each record with its variant type and (for SNPs) Ts/Tv class."""
    for record in records:
        variant_type = classify_variant(record.ref, record.alt)
        transition = is_transition(record.ref, record.alt) if variant_type == "SNP" else None
        yield VariantAnnotation(record=record, variant_type=variant_type, is_transition=transition)


def summarize_annotations(annotations: Iterable[VariantAnnotation]) -> AnnotationSummary:
    """Reduce a stream of :class:`VariantAnnotation` into an :class:`AnnotationSummary`."""
    summary = AnnotationSummary()
    for annotation in annotations:
        summary.total += 1
        if annotation.variant_type == "SNP":
            summary.snp += 1
            if annotation.is_transition:
                summary.transitions += 1
            else:
                summary.transversions += 1
        elif annotation.variant_type == "INS":
            summary.insertion += 1
        elif annotation.variant_type == "DEL":
            summary.deletion += 1
        else:
            summary.mnv += 1
    return summary


def annotate_vcf(source: str | Path | TextIO) -> tuple[list[VariantAnnotation], AnnotationSummary]:
    """Parse and annotate a VCF, returning per-variant annotations and a summary."""
    annotations = list(annotate_variants(parse_vcf(source)))
    summary = summarize_annotations(annotations)
    return annotations, summary


def write_multiqc_stats(
    summary: AnnotationSummary, sample_name: str, output_path: str | Path
) -> Path:
    """Write a summary JSON file consumable by the ``genomics_utils`` MultiQC module.

    The MultiQC plugin (see :mod:`genomics_utils.multiqc_plugin.genomics_module`)
    looks for files matching ``*_genomics_utils.json`` and expects this shape.
    """
    output_path = Path(output_path)
    payload = {"sample_name": sample_name, **summary.as_dict()}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
