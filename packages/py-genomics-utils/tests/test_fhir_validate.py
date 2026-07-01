import json
from pathlib import Path

import pytest

from genomics_utils.fhir_validate import validate_resource, validate_resource_file

DATA_DIR = Path(__file__).parent / "data"
PATIENT_EXAMPLE = DATA_DIR / "sample_fhir_patient.json"
OBSERVATION_EXAMPLE = DATA_DIR / "sample_fhir_observation.json"


def test_official_patient_example_is_valid():
    result = validate_resource_file(PATIENT_EXAMPLE)
    assert result.valid is True
    assert result.resource_type == "Patient"
    assert result.errors == []


def test_official_observation_example_is_valid():
    result = validate_resource_file(OBSERVATION_EXAMPLE)
    assert result.valid is True
    assert result.resource_type == "Observation"
    assert result.errors == []


def test_validate_resource_accepts_dict_directly():
    data = json.loads(OBSERVATION_EXAMPLE.read_text(encoding="utf-8"))
    result = validate_resource(data)
    assert result.valid is True


def test_missing_resource_type_is_invalid():
    result = validate_resource({"id": "no-type"})
    assert result.valid is False
    assert result.resource_type is None
    assert "resourceType" in result.errors[0]


def test_unsupported_resource_type_is_invalid():
    result = validate_resource({"resourceType": "Encounter"})
    assert result.valid is False
    assert result.resource_type == "Encounter"
    assert "Encounter" in result.errors[0]


def test_observation_missing_status_is_invalid():
    data = {
        "resourceType": "Observation",
        "code": {"coding": [{"system": "http://loinc.org", "code": "29463-7"}]},
    }
    result = validate_resource(data)
    assert result.valid is False
    assert any("status" in err for err in result.errors)


def test_observation_invalid_status_value_is_invalid():
    data = {
        "resourceType": "Observation",
        "status": "not-a-real-status",
        "code": {"coding": [{"system": "http://loinc.org", "code": "29463-7"}]},
    }
    result = validate_resource(data)
    assert result.valid is False
    assert any("status" in err for err in result.errors)


def test_observation_missing_code_is_invalid():
    data = {"resourceType": "Observation", "status": "final"}
    result = validate_resource(data)
    assert result.valid is False
    assert any("code" in err for err in result.errors)


def test_patient_with_no_optional_fields_is_valid():
    result = validate_resource({"resourceType": "Patient"})
    assert result.valid is True
    assert result.errors == []


def test_patient_invalid_gender_is_invalid():
    result = validate_resource({"resourceType": "Patient", "gender": "not-a-gender"})
    assert result.valid is False
    assert any("gender" in err for err in result.errors)


def test_patient_invalid_birth_date_is_invalid():
    result = validate_resource({"resourceType": "Patient", "birthDate": "not-a-date"})
    assert result.valid is False
    assert any("birthDate" in err for err in result.errors)


def test_patient_invalid_name_shape_is_invalid():
    result = validate_resource({"resourceType": "Patient", "name": "not-a-list"})
    assert result.valid is False
    assert any("name" in err for err in result.errors)


def test_validate_resource_ignores_unmodeled_fields():
    # Real-world resources carry many fields we don't model (identifier,
    # telecom, address, ...). They must not cause validation to fail.
    result = validate_resource(
        {
            "resourceType": "Patient",
            "identifier": [{"system": "urn:oid:1.2.3", "value": "12345"}],
            "telecom": [{"system": "phone", "value": "555-1234"}],
        }
    )
    assert result.valid is True


@pytest.mark.parametrize("bad_input", [None, [], "not-a-dict", 42])
def test_validate_resource_rejects_non_dict_input(bad_input):
    result = validate_resource(bad_input)
    assert result.valid is False
    assert result.resource_type is None
