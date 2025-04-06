import pytest
import re

from modules.backend_tests import AsteroidRequestBuilder
from core import ResponseKeys, AsteroidDataFields, FULLNAME_REGEX_PATTERN
from modules.backend_tests.tests.tests_asteroid_api.test_data import (
    VALID_DATA_TYPES_DATES
)


@pytest.mark.validation
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_fullname_parameter_returns_full_names(helper_asteroid, label, start, end):
    """Validate fullname=true returns extended designations (parenthesized name)."""
    pytest.logger.info(f"[{label}] Testing fullname=true flag with date range {start} to {end}")

    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_fullname()
        .build()
    )
    result = helper_asteroid.fetch_data(**params)
    sample = result.get(ResponseKeys.DATA.value, [])[0]

    pytest.logger.debug(f"Sample entry: {sample}")
    full_name = sample[-1].strip()  # the last item in sample '       (2024 AV2)  '
    assert re.match(FULLNAME_REGEX_PATTERN, full_name), f"Unexpected fullname format: {full_name}"


@pytest.mark.validation
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_diameter_field_included_when_enabled(helper_asteroid, label, start, end):
    """Ensure diameter field is included when requested (can be None if unknown)."""
    pytest.logger.info(f"[{label}] Requesting diameter=true with date range {start} to {end}")

    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_diameter()
        .build()
    )
    result = helper_asteroid.fetch_data(**params)
    sample = result.get(ResponseKeys.DATA.value, [])[0]

    pytest.logger.debug(f"Sample entry: {sample}")

    # Ensure the response structure includes the diameter field at index 12. This verifies the field is returned when
    # `diameter=true` is specified even if the value may be None (which is acceptable)
    assert len(sample) > AsteroidDataFields.DIAMETER
