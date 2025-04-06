import pytest

from test_data import *
from modules.backend_tests import AsteroidRequestBuilder
from core import HTTPStatusCodes, ResponseKeys, ASTEROID_API_SCHEMA, AsteroidDataFields, NASA_CLOSE_APPROACH_DATE_FORMAT
from datetime import datetime
from jsonschema import validate, ValidationError


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_cad_api_smoke_returns_basic_fields(helper_asteroid):
    """
    Basic smoke test: Ensure default request returns expected top-level keys.
    """
    result = helper_asteroid.fetch_data()

    for key in [ResponseKeys.COUNT.value, ResponseKeys.SIGNATURE.value, "fields", ResponseKeys.DATA.value]:
        assert key in result, f"Expected key '{key}' not found in response"


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_smoke_valid_date_filter_returns_data(helper_asteroid):
    """
    Smoke test: Ensure a valid date range returns a well-formed data list.
    """
    params = AsteroidRequestBuilder().with_date_range("2025-01-01", "2025-01-02").build()
    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.COUNT.value in result
    assert isinstance(result.get(ResponseKeys.DATA.value, []), list)


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_smoke_invalid_param_returns_400(helper_asteroid, faker_fixture):
    """
    Smoke test: Ensure invalid query param returns HTTP 400 and error message.
    """
    result = helper_asteroid.fetch_data(
        expected_status_code=HTTPStatusCodes.BAD_REQUEST.value,
        fakeparam=faker_fixture.first_name()
    )

    assert ResponseKeys.MESSAGE.value in result


@pytest.mark.smoke
@pytest.mark.validation
@pytest.mark.flaky_regression
def test_response_schema(helper_asteroid):
    """Validate overall response schema using JSON schema validation."""
    schema = ASTEROID_API_SCHEMA

    result = helper_asteroid.fetch_data()
    try:
        validate(instance=result, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed: {e}")


@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, has_data", DATE_RANGES)
def test_date_filter(helper_asteroid, label, start, end, has_data):
    """Verify that date range filters return appropriate data presence."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    if has_data:
        assert ResponseKeys.DATA.value in result
        assert isinstance(result[ResponseKeys.DATA.value], list)
        assert count > 0
    else:
        assert ResponseKeys.DATA.value not in result
        assert count == 0


@pytest.mark.flaky_regression
@pytest.mark.negative
@pytest.mark.parametrize("label, param, expected_error", INVALID_PARAMS)
def test_invalid_param(helper_asteroid, label, param, expected_error):
    """Check that invalid parameters return proper error messages."""
    result = helper_asteroid.fetch_data(expected_status_code=HTTPStatusCodes.BAD_REQUEST.value, **param)
    assert expected_error in result.get("message", "")


@pytest.mark.flaky_regression
@pytest.mark.edgecase
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_edge_case_no_data(helper_asteroid, label, start, end):
    """Confirm API returns zero results for extreme future date range."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_data_fields_have_expected_types(helper_asteroid, label, start, end):
    """Validate expected types for key fields in a known data window."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    data = result.get(ResponseKeys.DATA.value, [])
    assert isinstance(data, list), "'data' field should be a list"

    if data:
        first_entry = data[0]
        assert isinstance(first_entry[AsteroidDataFields.DES], str), f"{AsteroidDataFields.DES.name} should be a string"
        assert isinstance(first_entry[AsteroidDataFields.CD], str), f"{AsteroidDataFields.CD.name} should be a string"
        assert float(first_entry[AsteroidDataFields.DIST]) >= 0, \
            f"{AsteroidDataFields.DIST.name} should be a positive float"


@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist", DISTANCES)
def test_filter_by_distance(helper_asteroid, label, dist):
    """Ensure distance filter reduces or limits result set."""
    params = AsteroidRequestBuilder().with_dist_max(dist).build()
    result = helper_asteroid.fetch_data(**params)
    assert ResponseKeys.DATA.value in result


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_results_sorted_by_close_approach_date(helper_asteroid, label, start, end):
    """Check that results are sorted by close-approach date ascending."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    dates = [entry[AsteroidDataFields.CD] for entry in result.get(ResponseKeys.DATA.value, [])]

    parsed_dates = [datetime.strptime(date, NASA_CLOSE_APPROACH_DATE_FORMAT) for date in dates]
    assert parsed_dates == sorted(parsed_dates)


@pytest.mark.edgecase
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_empty_ranges_return_no_data(helper_asteroid, label, start, end):
    """Verify empty data sets return zero count and no data array."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0
    assert not result.get(ResponseKeys.DATA.value, [])


@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, dist", COMBINED_DATA_AND_DISTANCE)
def test_combined_date_and_distance_filter(helper_asteroid, label, start, end, dist):
    """Test combined filtering with both date range and maximum distance."""
    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_dist_max(dist)
        .build()
    )

    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.DATA.value in result, "Missing 'data' key in response"
    data = result[ResponseKeys.DATA.value]
    assert isinstance(data, list), "'data' field is not a list"

    max_dist = float(dist)

    for i, entry in enumerate(data):
        try:
            approach_distance = float(entry[AsteroidDataFields.DIST])
        except (ValueError, IndexError) as e:
            pytest.fail(f"Invalid distance value at row {i}: {entry} ({e})")

        assert approach_distance <= max_dist, (
            f"Entry {i} exceeds max distance: {approach_distance} > {max_dist} (entry: {entry})"
        )


@pytest.mark.flaky_regression
# @pytest.mark.skip(reason="Intentional overloading of the API")
def test_simulate_rate_limit(helper_asteroid, helper_thread):
    """Simulate API 503 by rapid fire calls (skipped by default)."""

    successes, failures, others = helper_thread.simulate_asteroid_load(
        controller=helper_asteroid.controller,
        expected_success=HTTPStatusCodes.OK.value,
        expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value
    )

    pytest.logger.info(
        f"[Threaded Rate Limit] {successes} successful | {failures} failed (503s) | {others} other"
    )

    assert failures >= 1, (
        f"Expected at least one {HTTPStatusCodes.SERVICE_UNAVAILABLE.value} error under load"
    )
import pytest

from test_data import *
from modules.backend_tests import AsteroidRequestBuilder
from core import HTTPStatusCodes, ResponseKeys, ASTEROID_API_SCHEMA, AsteroidDataFields, NASA_CLOSE_APPROACH_DATE_FORMAT
from datetime import datetime
from jsonschema import validate, ValidationError


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_cad_api_smoke_returns_basic_fields(helper_asteroid):
    """
    Basic smoke test: Ensure default request returns expected top-level keys.
    """
    result = helper_asteroid.fetch_data()

    for key in [ResponseKeys.COUNT.value, ResponseKeys.SIGNATURE.value, "fields", ResponseKeys.DATA.value]:
        assert key in result, f"Expected key '{key}' not found in response"


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_smoke_valid_date_filter_returns_data(helper_asteroid):
    """
    Smoke test: Ensure a valid date range returns a well-formed data list.
    """
    params = AsteroidRequestBuilder().with_date_range("2025-01-01", "2025-01-02").build()
    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.COUNT.value in result
    assert isinstance(result.get(ResponseKeys.DATA.value, []), list)


@pytest.mark.smoke
@pytest.mark.flaky_regression
def test_smoke_invalid_param_returns_400(helper_asteroid, faker_fixture):
    """
    Smoke test: Ensure invalid query param returns HTTP 400 and error message.
    """
    result = helper_asteroid.fetch_data(
        expected_status_code=HTTPStatusCodes.BAD_REQUEST.value,
        fakeparam=faker_fixture.first_name()
    )

    assert ResponseKeys.MESSAGE.value in result


@pytest.mark.smoke
@pytest.mark.validation
@pytest.mark.flaky_regression
def test_response_schema(helper_asteroid):
    """Validate overall response schema using JSON schema validation."""
    schema = ASTEROID_API_SCHEMA

    result = helper_asteroid.fetch_data()
    try:
        validate(instance=result, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed: {e}")


@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, has_data", DATE_RANGES)
def test_date_filter(helper_asteroid, label, start, end, has_data):
    """Verify that date range filters return appropriate data presence."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    if has_data:
        assert ResponseKeys.DATA.value in result
        assert isinstance(result[ResponseKeys.DATA.value], list)
        assert count > 0
    else:
        assert ResponseKeys.DATA.value not in result
        assert count == 0


@pytest.mark.flaky_regression
@pytest.mark.negative
@pytest.mark.parametrize("label, param, expected_error", INVALID_PARAMS)
def test_invalid_param(helper_asteroid, label, param, expected_error):
    """Check that invalid parameters return proper error messages."""
    result = helper_asteroid.fetch_data(expected_status_code=HTTPStatusCodes.BAD_REQUEST.value, **param)
    assert expected_error in result.get("message", "")


@pytest.mark.flaky_regression
@pytest.mark.edgecase
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_edge_case_no_data(helper_asteroid, label, start, end):
    """Confirm API returns zero results for extreme future date range."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_DATA_TYPES_DATES)
def test_data_fields_have_expected_types(helper_asteroid, label, start, end):
    """Validate expected types for key fields in a known data window."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    data = result.get(ResponseKeys.DATA.value, [])
    assert isinstance(data, list), "'data' field should be a list"

    if data:
        first_entry = data[0]
        assert isinstance(first_entry[AsteroidDataFields.DES], str), f"{AsteroidDataFields.DES.name} should be a string"
        assert isinstance(first_entry[AsteroidDataFields.CD], str), f"{AsteroidDataFields.CD.name} should be a string"
        assert float(first_entry[AsteroidDataFields.DIST]) >= 0, \
            f"{AsteroidDataFields.DIST.name} should be a positive float"


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist", DISTANCES)
def test_filter_by_distance(helper_asteroid, label, dist):
    """Ensure distance filter reduces or limits result set."""
    params = AsteroidRequestBuilder().with_dist_max(dist).build()
    result = helper_asteroid.fetch_data(**params)
    assert ResponseKeys.DATA.value in result


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_results_sorted_by_close_approach_date(helper_asteroid, label, start, end):
    """Check that results are sorted by close-approach date ascending."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    dates = [entry[AsteroidDataFields.CD] for entry in result.get(ResponseKeys.DATA.value, [])]

    parsed_dates = [datetime.strptime(date, NASA_CLOSE_APPROACH_DATE_FORMAT) for date in dates]
    assert parsed_dates == sorted(parsed_dates)


@pytest.mark.edgecase
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_empty_ranges_return_no_data(helper_asteroid, label, start, end):
    """Verify empty data sets return zero count and no data array."""
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)
    assert result.get(ResponseKeys.COUNT.value) == 0
    assert not result.get(ResponseKeys.DATA.value, [])


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, dist", COMBINED_DATA_AND_DISTANCE)
def test_combined_date_and_distance_filter(helper_asteroid, label, start, end, dist):
    """Test combined filtering with both date range and maximum distance."""
    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_dist_max(dist)
        .build()
    )

    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.DATA.value in result, "Missing 'data' key in response"
    data = result[ResponseKeys.DATA.value]
    assert isinstance(data, list), "'data' field is not a list"

    max_dist = float(dist)

    for i, entry in enumerate(data):
        try:
            approach_distance = float(entry[AsteroidDataFields.DIST])
        except (ValueError, IndexError) as e:
            pytest.fail(f"Invalid distance value at row {i}: {entry} ({e})")

        assert approach_distance <= max_dist, (
            f"Entry {i} exceeds max distance: {approach_distance} > {max_dist} (entry: {entry})"
        )


@pytest.mark.load
@pytest.mark.flaky_regression
# @pytest.mark.skip(reason="Intentional overloading of the API")
def test_simulate_rate_limit(helper_asteroid, helper_thread):
    """Simulate API 503 by rapid fire calls (skipped by default)."""

    successes, failures, others = helper_thread.simulate_asteroid_load(
        controller=helper_asteroid.controller,
        expected_success=HTTPStatusCodes.OK.value,
        expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value
    )

    pytest.logger.info(
        f"[Threaded Rate Limit] {successes} successful | {failures} failed (503s) | {others} other"
    )

    assert failures >= 1, (
        f"Expected at least one {HTTPStatusCodes.SERVICE_UNAVAILABLE.value} error under load"
    )
