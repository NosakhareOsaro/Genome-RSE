"""Flask REST API serving structural-variant records for jbrowse2-sv-tracks.

See sv_source.py for the VCF-parsing logic this API wraps. CORS is
enabled permissively (`CORS(app)`) since this is a public demo API with
no sensitive data, consumed cross-origin by the JBrowse2 plugin running
on a different host/port (local dev server or GitHub Pages) -- this is
not general guidance for an API serving private data.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from sv_source import get_svs


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/svs")
    def svs():
        ref_name = request.args.get("refName")
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        if ref_name is None or start is None or end is None:
            return jsonify({"error": "refName, start, and end query params are required"}), 400
        if start < 0 or end < start:
            return jsonify({"error": "invalid region: end must be >= start >= 0"}), 400

        return jsonify(get_svs(ref_name, start, end))

    return app


app = create_app()
