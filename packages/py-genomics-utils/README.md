# genomics-utils

Small, focused bioinformatics utilities used as a Phase 1 portfolio package:

1. **VCF annotation helper** — parses a VCF file, classifies each variant
   (SNP / insertion / deletion / MNV), computes transition/transversion
   stats, and can emit a small JSON summary.
2. **FHIR resource validator** — structural validation of a minimal subset
   of FHIR R4 `Patient` and `Observation` resources.
3. **MultiQC plugin** — a MultiQC module that visualizes the VCF annotation
   summary JSON in a MultiQC report.

## Installation

```bash
pip install -e ".[dev,docs]"
```

## Components

### VCF annotation helper

See `genomics_utils.vcf_annotate`. Operates on a small, hand-authored
synthetic VCF (see `tests/data/README.md`) purely for demonstration and
testing — it is not a production-grade annotation engine (no external
annotation database lookups, no INFO/CSQ field parsing beyond what is
generated locally).

### FHIR resource validator

See `genomics_utils.fhir_validate`.

> **Scope note:** this validator only checks that a JSON document has the
> *shape* of a minimal FHIR R4 `Patient` or `Observation` resource
> (required fields present, correct basic types). It does **not** perform
> full FHIR conformance validation — it does not check terminology
> bindings (e.g. that a `code` comes from a real code system), does not
> validate against StructureDefinition profiles, and does not check
> referential integrity between resources. For conformance-grade
> validation, use the official [HL7 FHIR validator](https://confluence.hl7.org/display/FHIR/Using+the+FHIR+Validator).

### MultiQC plugin

See `genomics_utils.multiqc_plugin.genomics_module`. Registered via the
`multiqc.modules.v1` entry point, it looks for `*_genomics_utils.json`
summary files (written by the VCF annotation helper) and renders variant
counts and a Ts/Tv ratio in the MultiQC report.

## Sample data

All test fixtures under `tests/data/` are either hand-authored synthetic
data or minimal official examples pulled from public specifications — see
`tests/data/README.md` for exact provenance of each file.
