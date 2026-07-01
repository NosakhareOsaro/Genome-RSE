"""Sphinx configuration for genomics-utils."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

from genomics_utils import __version__  # noqa: E402

project = "genomics-utils"
copyright = "2026, Nosakhare Osaro"
author = "Nosakhare Osaro"
release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"

# multiqc pulls in a large dependency chain (numpy, matplotlib, ...) that
# isn't needed to render docstrings/signatures, and has been observed to
# fail to import cleanly under Sphinx's autodoc reload machinery on some
# environments. Mock it out rather than fully installing/importing it.
autodoc_mock_imports = ["multiqc"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_theme = "sphinx_rtd_theme"
html_static_path = []
