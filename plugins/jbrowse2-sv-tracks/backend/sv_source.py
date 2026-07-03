"""Structural-variant VCF parsing for the sv-tracks-backend API.

Wraps pysam to turn VCF SV records (DEL/DUP/INV symbolic ALTs and BND
breakend notation) into plain JSON-serializable dicts with both
breakpoints, so the JBrowse2 plugin can draw an arc between them
regardless of SV type: for DEL/DUP/INV the "mate" is the variant's own
END (an arc spanning the event); for BND it's the linked mate breakend,
possibly on a different contig.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pysam

BND_RE = re.compile(r"[\[\]](?P<chrom>[^:\[\]]+):(?P<pos>\d+)[\[\]]")

DEFAULT_VCF_PATH = Path(__file__).parent / "data" / "sv-demo.vcf.gz"


def parse_bnd_mate(alt: str) -> tuple[str, int] | None:
    """Extract (chrom, 1-based pos) of the mate breakend from ALT notation.

    E.g. ``N[ctgB:3000[`` or ``]ctgA:40000]N`` -> ``("ctgB", 3000)`` /
    ``("ctgA", 40000)``. Returns None if `alt` isn't breakend notation.
    """
    match = BND_RE.search(alt)
    if match is None:
        return None
    return match.group("chrom"), int(match.group("pos"))


def _record_to_dict(record: "pysam.VariantRecord") -> dict[str, Any] | None:
    info = dict(record.info)
    sv_type = info.get("SVTYPE")
    if sv_type is None:
        return None

    alts = record.alts
    alt = alts[0] if alts else None

    if sv_type == "BND":
        if alt is None:
            return None
        mate = parse_bnd_mate(alt)
        if mate is None:
            return None
        mate_ref_name, mate_pos = mate
        mate_start, mate_end = mate_pos - 1, mate_pos
    else:
        # VCF's END is a reserved INFO key that pysam/htslib surfaces via
        # record.stop (0-based, exclusive) rather than record.info["END"].
        mate_ref_name = record.chrom
        mate_start, mate_end = record.stop - 1, record.stop

    return {
        "id": record.id or f"{record.chrom}:{record.pos}",
        "refName": record.chrom,
        "start": record.pos - 1,
        "end": record.pos,
        "mateRefName": mate_ref_name,
        "mateStart": mate_start,
        "mateEnd": mate_end,
        "svType": sv_type,
    }


def get_svs(
    ref_name: str,
    start: int,
    end: int,
    vcf_path: Path | str = DEFAULT_VCF_PATH,
) -> list[dict[str, Any]]:
    """Return SV records overlapping [start, end) (0-based, half-open) on ref_name.

    Returns an empty list if `ref_name` isn't a contig in the VCF.
    """
    records: list[dict[str, Any]] = []
    with pysam.VariantFile(str(vcf_path)) as vcf:
        if ref_name not in vcf.header.contigs:
            return records
        for rec in vcf.fetch(ref_name, start, end):
            parsed = _record_to_dict(rec)
            if parsed is not None:
                records.append(parsed)
    return records
