"""Flask REST API serving structural-variant records for jbrowse2-sv-tracks.

See sv_source.py for the VCF-parsing logic this API wraps.
"""

from __future__ import annotations

from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    return app


app = create_app()
