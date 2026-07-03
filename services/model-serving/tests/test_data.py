from pathlib import Path

import pytest

from training.data import SEQUENCE_LENGTH, VALID_CLASSES, load_splice_records


def test_load_splice_records_from_cached_file() -> None:
    records = load_splice_records()
    assert len(records) == 3190
    labels = {record.label for record in records}
    assert labels == set(VALID_CLASSES)
    assert all(len(record.sequence) == SEQUENCE_LENGTH for record in records)


def test_load_splice_records_uppercases_sequence(tmp_path: Path) -> None:
    data_file = tmp_path / "mini.data"
    data_file.write_text("EI, TEST-1, " + ("acgt" * 15) + "\n")
    records = load_splice_records(data_file)
    assert records[0].sequence == ("ACGT" * 15)


def test_load_splice_records_rejects_bad_label(tmp_path: Path) -> None:
    data_file = tmp_path / "bad.data"
    data_file.write_text("XX, TEST-1, " + ("A" * SEQUENCE_LENGTH) + "\n")
    with pytest.raises(ValueError, match="unknown class label"):
        load_splice_records(data_file)


def test_load_splice_records_rejects_wrong_length(tmp_path: Path) -> None:
    data_file = tmp_path / "short.data"
    data_file.write_text("N, TEST-1, ACGT\n")
    with pytest.raises(ValueError, match="expected a 60-nucleotide sequence"):
        load_splice_records(data_file)


def test_load_splice_records_rejects_wrong_field_count(tmp_path: Path) -> None:
    data_file = tmp_path / "malformed.data"
    data_file.write_text("N, TEST-1\n")
    with pytest.raises(ValueError, match="expected 3 comma-separated fields"):
        load_splice_records(data_file)


def test_load_splice_records_skips_blank_lines(tmp_path: Path) -> None:
    data_file = tmp_path / "blank.data"
    data_file.write_text("\nN, TEST-1, " + ("A" * SEQUENCE_LENGTH) + "\n\n")
    records = load_splice_records(data_file)
    assert len(records) == 1
