# Test data provenance

This service's tests don't use external fixture files -- all test
payloads (FHIR `MolecularSequence` JSON bodies, JWT claims, etc.) are
small, hand-authored Python literals defined inline in the test modules
under `tests/`. Field values (patient references, coordinate systems)
are illustrative placeholders, not sourced from any real dataset.
