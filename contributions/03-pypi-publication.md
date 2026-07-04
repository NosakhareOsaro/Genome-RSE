# WP4: PyPI publication of `genomerse-genomics-utils`

**Status:** Published, live.
**Artifact:** [pypi.org/project/genomerse-genomics-utils/0.1.0](https://pypi.org/project/genomerse-genomics-utils/0.1.0/)
**Published:** 2026-07-04

## What this is

[`packages/py-genomics-utils`](../packages/py-genomics-utils) -- the
Phase 1 Python package (VCF annotation, minimal FHIR R4 structural
validation, a MultiQC plugin), published to the real Python Package
Index so `pip install genomerse-genomics-utils` genuinely works from the
public internet, for anyone, with no access to this repo or any
GenomeRSE-specific tooling required.

## The rename: `genomics-utils` -> `genomerse-genomics-utils`

The package's existing name in `pyproject.toml` was `genomics-utils` --
confirmed available on PyPI (a real 404 on both the JSON API and the
authoritative Simple index, not assumed), but judged too generic for
this context before publishing under it. The reasoning: a reviewer
finding this package standalone on PyPI -- without necessarily having
read the GitHub repo first -- would get no signal from the bare name
that it's a small, demonstration-scoped portfolio package rather than a
general-purpose production library. The package's own README is
explicit about that scope ("not a production-grade annotation engine,"
"does not perform full FHIR conformance validation"), but that context
doesn't travel with a generic name on a package index. Renamed to
`genomerse-genomics-utils` before any registry upload -- nothing had
been published anywhere yet, so the rename cost nothing. Only the PyPI
distribution name changed; the Python import path stays `genomics_utils`
(the same pattern as, e.g., `python-dateutil` importing as `dateutil`),
so no code changed.

## Process

1. Confirmed both `genomics-utils` and the eventual `genomerse-genomics-utils`
   were available on PyPI *and* on test.pypi.org independently (separate
   namespaces, checked separately) before deciding anything.
2. Built the package (`python -m build`) and ran `twine check` -- the
   same tool PyPI itself uses to validate `long_description` rendering
   -- confirming the README renders cleanly before ever uploading
   anywhere.
3. **Dry-ran the full publish on test.pypi.org first**, under the final
   name (not a throwaway name), specifically so the rehearsal exercised
   the exact real command rather than a mechanically-similar but
   different one. Verified the dry run for real: installed into a
   completely fresh virtualenv from `test.pypi.org` (with
   `--extra-index-url` pointing at real PyPI for the package's actual
   dependencies, `pydantic`/`multiqc`, which test.pypi.org doesn't
   mirror), then called the real `annotate_vcf()` and `validate_resource()`
   functions against real sample inputs and asserted on the results --
   not just confirming the import resolved.
4. Only after that dry run passed cleanly did the real, irreversible
   `pypi.org` publish happen. PyPI's own deletion policy was checked
   directly beforehand (not assumed): "Deletion of a project, release or
   file on PyPI is permanent and irreversible, without exception" -- a
   deliberate pause point before running the real upload command.
5. Verified the real publish the same way as the dry run: fresh
   virtualenv, `pip install genomerse-genomics-utils` with no index
   overrides (the real, default public index), confirmed the install
   resolves to `site-packages` (not a local checkout), and re-ran the
   identical VCF-classification and FHIR-validation functional checks
   against the genuinely published package.

The test.pypi.org dry run is recorded here deliberately, not because it
needed hiding, but because using a staging index before an irreversible
publish is itself the kind of practice worth being able to point to.

## Why this matters

Publishing a real, installable package to PyPI is standard practice for
distributing Python software, not a novel contribution -- but it's a
genuine, independently checkable artifact: anyone, anywhere, can run
`pip install genomerse-genomics-utils` right now and get the real thing.
