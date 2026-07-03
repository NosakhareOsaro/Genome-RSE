# sv-tracks-backend

A small Flask REST API that serves structural-variant (SV) records
parsed from a VCF, for the `jbrowse2-sv-tracks` JBrowse2 plugin
(`../plugin/`) to consume and render as arcs.

## Endpoints

- `GET /api/health` — liveness check
- `GET /api/svs?refName=<name>&start=<int>&end=<int>` — SV records
  overlapping the given region, each with both breakpoints (for arc
  rendering) and an SV type

## Sample data

See `data/DATA_SOURCE.md` for exact provenance of every file in `data/`
— a mix of real public JBrowse2 demo data and hand-authored synthetic
SV records; the README there is unambiguous about which is which.

## Local development

```bash
pip install -e ".[dev]"
pytest
FLASK_APP=app.py flask run
```
