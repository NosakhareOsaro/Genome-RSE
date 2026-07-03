"""Generate demo/sv-demo.json: a static snapshot of every SV record in the
demo VCF, for the GitHub Pages demo to serve as a plain static file.

The GitHub Pages demo has no Flask backend to query, so it can't use
sv-tracks-backend's /api/svs endpoint directly. Instead, SvJsonAdapter's
own client-side region-overlap filtering (see plugin/src/util/region.js)
means a single static JSON file containing *all* records works exactly
the same way a real backend endpoint would from the adapter's point of
view -- the adapter just gets back more than it asked for and filters
locally.

Run from the demo/ directory:
    python build_static_svs.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sv_source import get_svs  # noqa: E402

VCF_PATH = Path(__file__).parent.parent / "backend" / "data" / "sv-demo.vcf.gz"
OUTPUT_PATH = Path(__file__).parent / "sv-demo.json"

CONTIGS = [
    ("ctgA", 50001),
    ("ctgB", 6079),
]


def main() -> None:
    records = []
    for ref_name, length in CONTIGS:
        records.extend(get_svs(ref_name, 0, length, vcf_path=VCF_PATH))
    OUTPUT_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} SV records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
