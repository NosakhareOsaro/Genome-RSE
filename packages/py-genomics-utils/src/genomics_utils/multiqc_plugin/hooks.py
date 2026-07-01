"""MultiQC plugin hook entry points for ``genomics_utils``.

Registered under the ``multiqc.hooks.v1`` entry point group and run by
MultiQC at its ``execution_start`` trigger — i.e. before file search runs.
This is where third-party MultiQC modules must register their search
patterns, since ``config.sp`` needs to be populated before MultiQC scans
the analysis directory for matching files.
"""

from __future__ import annotations

from multiqc import config


def register_search_patterns() -> None:
    """Register the file pattern used to find genomics_utils stats JSON files."""
    config.update_dict(config.sp, {"genomics_utils": {"fn": "*_genomics_utils.json"}})
