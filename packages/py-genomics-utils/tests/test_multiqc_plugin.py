import json

import pytest

import multiqc
from genomics_utils.multiqc_plugin.genomics_module import parse_stats_json
from genomics_utils.vcf_annotate import annotate_vcf, write_multiqc_stats

DATA_DIR = __import__("pathlib").Path(__file__).parent / "data"
SAMPLE_VCF = DATA_DIR / "sample.vcf"


def test_parse_stats_json_valid():
    raw = json.dumps(
        {
            "sample_name": "s1",
            "total": 6,
            "snp": 3,
            "insertion": 1,
            "deletion": 1,
            "mnv": 1,
            "transitions": 1,
            "transversions": 2,
            "ts_tv_ratio": 0.5,
        }
    )
    data = parse_stats_json(raw)
    assert data["sample_name"] == "s1"
    assert data["total"] == 6


def test_parse_stats_json_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        parse_stats_json("not json")


def test_parse_stats_json_missing_keys_raises():
    with pytest.raises(ValueError, match="missing required keys"):
        parse_stats_json(json.dumps({"sample_name": "s1"}))


@pytest.fixture(autouse=True)
def _reset_multiqc_report():
    multiqc.reset()
    yield
    multiqc.reset()


def test_multiqc_entry_point_is_registered():
    from importlib.metadata import entry_points

    names = {ep.name for ep in entry_points(group="multiqc.modules.v1")}
    assert "genomics_utils" in names


def test_multiqc_module_end_to_end(tmp_path):
    _, summary = annotate_vcf(SAMPLE_VCF)
    write_multiqc_stats(summary, sample_name="sample1", output_path=tmp_path / "sample1_genomics_utils.json")

    multiqc.parse_logs(tmp_path, run_modules=["genomics_utils"])

    module_data = multiqc.get_module_data(module="genomics_utils")
    sample_data = module_data["sample1"]
    assert sample_data["total"] == 6
    assert sample_data["snp"] == 3

    general_stats = multiqc.get_general_stats_data(sample="sample1")
    assert general_stats["Genomics Utils.total"] == 6


def test_multiqc_module_skips_malformed_file(tmp_path):
    (tmp_path / "broken_genomics_utils.json").write_text("not json", encoding="utf-8")
    multiqc.parse_logs(tmp_path, run_modules=["genomics_utils"])
    # The malformed file is skipped with a warning, leaving no samples, so
    # the module raises ModuleNoSamplesFound internally and never registers.
    with pytest.raises(ValueError, match="not found"):
        multiqc.get_module_data(module="genomics_utils")
