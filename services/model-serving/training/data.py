"""Load the cached UCI splice-junction dataset.

See ``data/DATA_SOURCE.md`` for provenance. The raw file is a
comma-separated, fixed-width text format that isn't quite CSV (fields are
padded with spaces), so this module handles the parsing rather than
reaching for ``pandas.read_csv`` directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "splice.data"

VALID_CLASSES = ("EI", "IE", "N")
SEQUENCE_LENGTH = 60


@dataclass(frozen=True)
class SpliceRecord:
    """One labeled instance from the dataset."""

    label: str
    instance_name: str
    sequence: str


def load_splice_records(path: Path | None = None) -> list[SpliceRecord]:
    """Parse ``splice.data`` into a list of :class:`SpliceRecord`.

    Raises ``ValueError`` on any row that doesn't match the expected
    ``label, instance_name, sequence`` shape -- this dataset is small and
    fully public, so a malformed row means something is wrong with the
    cached file, not a data-quality edge case to silently skip.
    """
    data_path = path or DEFAULT_DATA_PATH
    records: list[SpliceRecord] = []
    for line_number, raw_line in enumerate(data_path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 3:
            raise ValueError(
                f"{data_path}:{line_number}: expected 3 comma-separated "
                f"fields, got {len(fields)}"
            )
        label, instance_name, sequence = fields
        if label not in VALID_CLASSES:
            raise ValueError(f"{data_path}:{line_number}: unknown class label {label!r}")
        sequence = sequence.upper()
        if len(sequence) != SEQUENCE_LENGTH:
            raise ValueError(
                f"{data_path}:{line_number}: expected a {SEQUENCE_LENGTH}-"
                f"nucleotide sequence, got {len(sequence)}"
            )
        records.append(SpliceRecord(label=label, instance_name=instance_name, sequence=sequence))
    return records
