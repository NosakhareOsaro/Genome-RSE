"""A MultiQC module for the ``genomics_utils`` VCF annotation summary.

Registered via the ``multiqc.modules.v1`` entry point (see
``pyproject.toml``). It looks for JSON summary files matching
``*_genomics_utils.json`` — written by
:func:`genomics_utils.vcf_annotate.write_multiqc_stats` — and reports
variant-type counts and the Ts/Tv ratio.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from multiqc.base_module import BaseMultiqcModule, ModuleNoSamplesFound
from multiqc.plots import bargraph

log = logging.getLogger(__name__)

_REQUIRED_KEYS = ("sample_name", "total", "snp", "insertion", "deletion", "mnv")


def parse_stats_json(raw_text: str) -> dict[str, Any]:
    """Parse and validate one ``*_genomics_utils.json`` file's contents.

    Pulled out as a standalone function so it can be unit tested without
    needing a full MultiQC report/search context.

    Raises:
        ValueError: if the JSON is malformed or missing required keys.
    """
    data = json.loads(raw_text)
    missing = [key for key in _REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"genomics_utils stats JSON missing required keys: {missing}")
    return data


class MultiqcModule(BaseMultiqcModule):
    """MultiQC module that visualizes genomics_utils VCF annotation summaries."""

    def __init__(self) -> None:
        super().__init__(
            name="Genomics Utils",
            anchor="genomics_utils",
            info="VCF annotation summary statistics (variant types, Ts/Tv ratio).",
        )

        self.genomics_utils_data: dict[str, dict[str, Any]] = {}
        for f in self.find_log_files("genomics_utils", filehandles=True):
            self._parse_log(f)

        self.genomics_utils_data = self.ignore_samples(self.genomics_utils_data)

        if len(self.genomics_utils_data) == 0:
            raise ModuleNoSamplesFound

        log.info(f"Found {len(self.genomics_utils_data)} genomics_utils reports")

        self.add_software_version(None)
        self.write_data_file(self.genomics_utils_data, "multiqc_genomics_utils")
        self._general_stats_table()
        self.add_section(
            name="Variant Types",
            anchor="genomics_utils-variant-types",
            description="Counts of each variant type classified by the VCF annotation helper.",
            plot=self._variant_type_bargraph(),
        )

    def _parse_log(self, f: dict[str, Any]) -> None:
        try:
            data = parse_stats_json(f["f"].read())
        except (json.JSONDecodeError, ValueError) as exc:
            log.warning(f"Could not parse genomics_utils JSON '{f['fn']}': {exc}")
            return
        s_name = data["sample_name"]
        self.add_data_source(f, s_name)
        self.genomics_utils_data[s_name] = data

    def _general_stats_table(self) -> None:
        headers = {
            "total": {
                "title": "Variants",
                "description": "Total number of variants annotated",
                "min": 0,
                "scale": "Blues",
            },
            "ts_tv_ratio": {
                "title": "Ts/Tv",
                "description": "Transition/transversion ratio",
                "min": 0,
                "format": "{:,.2f}",
                "scale": "RdYlGn",
            },
        }
        self.general_stats_addcols(self.genomics_utils_data, headers)

    def _variant_type_bargraph(self):
        keys = {
            "snp": {"name": "SNP"},
            "insertion": {"name": "Insertion"},
            "deletion": {"name": "Deletion"},
            "mnv": {"name": "MNV"},
        }
        pconfig = {
            "id": "genomics_utils-variant-types-plot",
            "title": "Genomics Utils: Variant Types",
            "ylab": "# Variants",
        }
        return bargraph.plot(self.genomics_utils_data, keys, pconfig)
