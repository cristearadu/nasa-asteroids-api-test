import pytest
from jsonschema import validate, ValidationError
from pydantic import ValidationError as PydanticValidationError

from core import ASTEROID_API_SCHEMA, AsteroidDataFields
from modules.backend_tests import AsteroidRequestBuilder, VALID_DATA_TYPES_DATES


from core import CadEntry, ResponseKeys


@pytest.mark.smoke
@pytest.mark.validation
@pytest.mark.flaky_regression
def test_response_schema(helper_asteroid):
    """Validate overall response schema using JSON schema and pydantic validation."""
    schema = ASTEROID_API_SCHEMA
    pytest.logger.info("Validating response against JSON schema and CadEntry...")

    result = helper_asteroid.fetch_data()

    # validate using JSON Schema
    try:
        validate(instance=result, schema=schema)
        pytest.logger.info("JSON Schema validation passed.")
    except ValidationError as e:
        pytest.logger.error(f"JSON Schema validation failed: {e}")
        pytest.fail(f"JSON Schema validation failed: {e}")

    # validate each row using Pydantic by converting list to dict
    fields = result.get("fields", [])
    data = result.get(ResponseKeys.DATA.value, [])

    try:
        for row in data:
            entry_dict = dict(zip(fields, row))
            CadEntry.model_validate(entry_dict)
        pytest.logger.info("Pydantic CadEntry validation passed.")
    except PydanticValidationError as e:
        pytest.logger.error(f"Pydantic CadEntry validation failed: {e}")
        pytest.fail(f"Pydantic CadEntry validation failed: {e}")


@pytest.mark.validation
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_data_fields_have_expected_types(helper_asteroid, label, start, end):
    """Validate expected types for key fields in a known data window."""
    pytest.logger.info(f"[{label}] Validating data field types from {start} to {end}")

    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    data = result.get(ResponseKeys.DATA.value, [])
    assert isinstance(data, list), "'data' field should be a list"

    if not data:
        pytest.logger.warning(f"[{label}] No data returned for range {start} to {end}")
    else:
        first_entry = data[0]
        pytest.logger.debug(f"[{label}] Sample entry: {first_entry}")

        assert isinstance(first_entry[AsteroidDataFields.DES], str), f"{AsteroidDataFields.DES.name} should be a string"
        assert isinstance(first_entry[AsteroidDataFields.CD], str), f"{AsteroidDataFields.CD.name} should be a string"
        assert float(first_entry[AsteroidDataFields.DIST]) >= 0, \
            f"{AsteroidDataFields.DIST.name} should be a positive float"

        pytest.logger.info(f"[{label}] Field types successfully validated.")
