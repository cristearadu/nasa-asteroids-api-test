import pytest
from datetime import timedelta
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError

from modules.backend_tests import AsteroidRequestBuilder
from core import ASTEROID_API_SCHEMA, ResponseKeys, CadEntry, DATE_FORMAT_ISO


@pytest.mark.schema
@pytest.mark.validation
@pytest.mark.randomized
def test_randomized_param_schema_validation(helper_asteroid, faker_fixture):
    """
    Sends requests using randomized (but valid) parameters and validates
    both the overall JSON schema and per-entry fields using Pydantic.
    """
    start_date = faker_fixture.date_between(start_date="-5y", end_date="today")
    end_date = start_date + timedelta(days=365)

    start = start_date.strftime(DATE_FORMAT_ISO)
    end = end_date.strftime(DATE_FORMAT_ISO)

    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    try:
        validate(instance=result, schema=ASTEROID_API_SCHEMA)
    except JsonSchemaValidationError as e:
        pytest.fail(f"Randomized schema failed: {e}")

    fields = result.get("fields", [])
    for entry in result.get(ResponseKeys.DATA.value, []):
        entry_dict = dict(zip(fields, entry))
        try:
            CadEntry.model_validate(entry_dict)
        except PydanticValidationError as e:
            pytest.fail(f"Randomized entry failed CadEntry validation: {e}")
