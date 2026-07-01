# Test data provenance

## `sample.vcf`

**Synthetic / hand-authored.** Not derived from any real sample or public
dataset. It contains 6 small, deterministic variant records covering each
variant type the annotation helper classifies (SNP transition, SNP
transversion, insertion, deletion, and a multi-nucleotide variant), plus a
VCF 4.2 header. Used because it is small, fast, and gives exact expected
counts for unit tests.

## `sample_fhir_observation.json`

**Real, public.** A minimal `Observation` example resource taken from the
official HL7 FHIR R4 specification examples page:
<https://www.hl7.org/fhir/R4/observation-example.json.html>
(retrieved 2026-07-01). Used as-is (only whitespace/formatting normalized)
so the validator is tested against a realistic, spec-authored resource
rather than an invented one.

## `sample_fhir_patient.json`

**Real, public.** A minimal `Patient` example resource taken from the
official HL7 FHIR R4 specification examples page:
<https://www.hl7.org/fhir/R4/patient-example.json.html>
(retrieved 2026-07-01). Used as-is (only whitespace/formatting normalized).
