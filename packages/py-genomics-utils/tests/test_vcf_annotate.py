import json
from pathlib import Path

import pytest

from genomics_utils.vcf_annotate import (
    AnnotationSummary,
    annotate_vcf,
    classify_variant,
    is_transition,
    parse_vcf,
    write_multiqc_stats,
)

DATA_DIR = Path(__file__).parent / "data"
SAMPLE_VCF = DATA_DIR / "sample.vcf"


def test_parse_vcf_reads_all_data_lines():
    records = list(parse_vcf(SAMPLE_VCF))
    assert len(records) == 6
    first = records[0]
    assert first.chrom == "chr1"
    assert first.pos == 100
    assert first.id == "rs1"
    assert first.ref == "A"
    assert first.alt == "G"
    assert first.qual == "50"
    assert first.filter == "PASS"
    assert first.info == {}


def test_parse_vcf_accepts_open_file_handle():
    with open(SAMPLE_VCF, encoding="utf-8") as handle:
        records = list(parse_vcf(handle))
    assert len(records) == 6


def test_parse_vcf_parses_info_field(tmp_path):
    vcf_path = tmp_path / "info.vcf"
    vcf_path.write_text("chr1\t1\t.\tA\tG\t.\tPASS\tDP=10;FLAG\n", encoding="utf-8")
    (record,) = list(parse_vcf(vcf_path))
    assert record.info == {"DP": "10", "FLAG": ""}


def test_parse_vcf_rejects_multiallelic(tmp_path):
    vcf_path = tmp_path / "multi.vcf"
    vcf_path.write_text("chr1\t1\t.\tA\tG,T\t.\tPASS\t.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Multi-allelic"):
        list(parse_vcf(vcf_path))


def test_parse_vcf_rejects_malformed_line(tmp_path):
    vcf_path = tmp_path / "bad.vcf"
    vcf_path.write_text("chr1\t1\t.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed VCF line"):
        list(parse_vcf(vcf_path))


@pytest.mark.parametrize(
    ("ref", "alt", "expected"),
    [
        ("A", "G", "SNP"),
        ("C", "A", "SNP"),
        ("A", "ATT", "INS"),
        ("GTA", "G", "DEL"),
        ("AC", "GT", "MNV"),
    ],
)
def test_classify_variant(ref, alt, expected):
    assert classify_variant(ref, alt) == expected


@pytest.mark.parametrize(
    ("ref", "alt", "expected"),
    [
        ("A", "G", True),  # purine -> purine
        ("G", "A", True),  # purine -> purine
        ("C", "T", True),  # pyrimidine -> pyrimidine
        ("C", "A", False),  # pyrimidine -> purine
        ("G", "T", False),  # purine -> pyrimidine
    ],
)
def test_is_transition(ref, alt, expected):
    assert is_transition(ref, alt) is expected


def test_annotate_vcf_summary_counts():
    annotations, summary = annotate_vcf(SAMPLE_VCF)
    assert len(annotations) == 6
    assert summary == AnnotationSummary(
        total=6,
        snp=3,
        insertion=1,
        deletion=1,
        mnv=1,
        transitions=1,
        transversions=2,
    )
    assert summary.ts_tv_ratio == pytest.approx(0.5)


def test_annotate_vcf_annotation_details():
    annotations, _ = annotate_vcf(SAMPLE_VCF)
    by_id = {a.record.id: a for a in annotations}
    assert by_id["rs1"].variant_type == "SNP"
    assert by_id["rs1"].is_transition is True
    assert by_id["rs2"].is_transition is False
    assert by_id["rs4"].variant_type == "INS"
    assert by_id["rs4"].is_transition is None
    assert by_id["rs5"].variant_type == "DEL"
    assert by_id["rs6"].variant_type == "MNV"


def test_summary_ts_tv_ratio_none_when_no_transversions():
    summary = AnnotationSummary(total=1, snp=1, transitions=1, transversions=0)
    assert summary.ts_tv_ratio is None


def test_write_multiqc_stats(tmp_path):
    _, summary = annotate_vcf(SAMPLE_VCF)
    output_path = tmp_path / "sample_genomics_utils.json"
    result_path = write_multiqc_stats(summary, sample_name="sample", output_path=output_path)

    assert result_path == output_path
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["sample_name"] == "sample"
    assert payload["total"] == 6
    assert payload["snp"] == 3
    assert payload["ts_tv_ratio"] == pytest.approx(0.5)
