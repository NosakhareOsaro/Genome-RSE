from pathlib import Path

import pysam
import pytest

from sv_source import get_svs, parse_bnd_mate

DATA_DIR = Path(__file__).parent.parent / "data"
DEMO_VCF = DATA_DIR / "sv-demo.vcf.gz"


@pytest.mark.parametrize(
    ("alt", "expected"),
    [
        ("N[ctgB:3000[", ("ctgB", 3000)),
        ("]ctgA:40000]N", ("ctgA", 40000)),
        ("[ctg_1:42[N", ("ctg_1", 42)),
        ("<DEL>", None),
        ("A", None),
    ],
)
def test_parse_bnd_mate(alt, expected):
    assert parse_bnd_mate(alt) == expected


def test_get_svs_returns_all_four_types_on_ctga():
    records = get_svs("ctgA", 0, 50001, vcf_path=DEMO_VCF)
    types_by_id = {r["id"]: r["svType"] for r in records}
    assert types_by_id == {
        "sv1_del": "DEL",
        "sv2_dup": "DUP",
        "sv3_inv": "INV",
        "sv4_bnd_1": "BND",
    }


def test_get_svs_del_has_matching_span_as_mate():
    (record,) = [r for r in get_svs("ctgA", 9000, 13000, vcf_path=DEMO_VCF) if r["id"] == "sv1_del"]
    assert record["refName"] == "ctgA"
    assert record["start"] == 9999
    assert record["end"] == 10000
    assert record["mateRefName"] == "ctgA"
    assert record["mateStart"] == 11999
    assert record["mateEnd"] == 12000


def test_get_svs_bnd_mate_is_on_different_contig():
    (record,) = [r for r in get_svs("ctgA", 0, 50001, vcf_path=DEMO_VCF) if r["id"] == "sv4_bnd_1"]
    assert record["refName"] == "ctgA"
    assert record["mateRefName"] == "ctgB"
    assert record["mateStart"] == 2999
    assert record["mateEnd"] == 3000


def test_get_svs_bnd_pair_is_reciprocal():
    (fwd,) = [r for r in get_svs("ctgA", 0, 50001, vcf_path=DEMO_VCF) if r["id"] == "sv4_bnd_1"]
    (rev,) = [r for r in get_svs("ctgB", 0, 6079, vcf_path=DEMO_VCF) if r["id"] == "sv4_bnd_2"]
    assert fwd["refName"] == rev["mateRefName"]
    assert fwd["start"] == rev["mateStart"]
    assert rev["refName"] == fwd["mateRefName"]
    assert rev["start"] == fwd["mateStart"]


def test_get_svs_filters_by_region():
    ids = {r["id"] for r in get_svs("ctgA", 15000, 20000, vcf_path=DEMO_VCF)}
    assert ids == {"sv2_dup"}


def test_get_svs_unknown_contig_returns_empty():
    assert get_svs("does-not-exist", 0, 100, vcf_path=DEMO_VCF) == []


def test_get_svs_region_with_no_svs_returns_empty():
    assert get_svs("ctgA", 0, 100, vcf_path=DEMO_VCF) == []


def test_get_svs_skips_records_without_svtype(tmp_path):
    vcf_text = (
        "##fileformat=VCFv4.2\n"
        "##contig=<ID=ctgA,length=50001>\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "ctgA\t100\tplain_snv\tA\tG\t.\tPASS\t.\n"
    )
    raw_vcf = tmp_path / "no_svtype.vcf"
    raw_vcf.write_text(vcf_text)
    gz_path = tmp_path / "no_svtype.vcf.gz"
    pysam.tabix_compress(str(raw_vcf), str(gz_path))
    pysam.tabix_index(str(gz_path), preset="vcf")

    assert get_svs("ctgA", 0, 200, vcf_path=gz_path) == []


def test_get_svs_skips_bnd_with_no_alt(tmp_path):
    vcf_text = (
        "##fileformat=VCFv4.2\n"
        "##contig=<ID=ctgA,length=50001>\n"
        '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="d">\n'
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "ctgA\t100\tno_alt_bnd\tA\t.\t.\tPASS\tSVTYPE=BND\n"
    )
    raw_vcf = tmp_path / "no_alt_bnd.vcf"
    raw_vcf.write_text(vcf_text)
    gz_path = tmp_path / "no_alt_bnd.vcf.gz"
    pysam.tabix_compress(str(raw_vcf), str(gz_path))
    pysam.tabix_index(str(gz_path), preset="vcf")

    assert get_svs("ctgA", 0, 200, vcf_path=gz_path) == []


def test_get_svs_skips_bnd_with_unparseable_alt(tmp_path):
    vcf_text = (
        "##fileformat=VCFv4.2\n"
        "##contig=<ID=ctgA,length=50001>\n"
        '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="d">\n'
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "ctgA\t100\tbad_bnd\tA\t<BND>\t.\tPASS\tSVTYPE=BND\n"
    )
    raw_vcf = tmp_path / "bad_bnd.vcf"
    raw_vcf.write_text(vcf_text)
    gz_path = tmp_path / "bad_bnd.vcf.gz"
    pysam.tabix_compress(str(raw_vcf), str(gz_path))
    pysam.tabix_index(str(gz_path), preset="vcf")

    assert get_svs("ctgA", 0, 200, vcf_path=gz_path) == []
