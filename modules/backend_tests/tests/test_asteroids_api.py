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
    pytest.logger.info("Fetched default response from CAD API.")

    for key in [ResponseKeys.COUNT.value, ResponseKeys.SIGNATURE.value, "fields", ResponseKeys.DATA.value]:
        assert key in result, f"Expected key '{key}' not found in response"
        pytest.logger.debug(f"Verified presence of key: {key}")


@pytest.mark.smoke
@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, has_data", DATE_RANGES)
def test_smoke_valid_date_filter_returns_data(helper_asteroid, label, start, end, has_data):
    """
    Smoke test: Ensure a valid date range returns a well-formed data list.
    """
    pytest.logger.info(f"[{label}] Testing date range: {start} → {end}")

    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    data = result.get(ResponseKeys.DATA.value)

    if ResponseKeys.COUNT.value not in result:
        pytest.logger.warning(f"[{label}] Missing 'count' in response.")

    if has_data:
        assert data is not None, f"[{label}] Expected 'data' key missing."
        assert isinstance(data, list), f"[{label}] 'data' is not a list."
        assert count > 0, f"[{label}] Expected count > 0 but got {count}."
    else:
        assert data is None or data == [], f"[{label}] Expected no data, but got: {data}"
        assert count == 0, f"[{label}] Expected count == 0, but got {count}"

    pytest.logger.info(f"[{label}] Date filter passed")


@pytest.mark.smoke
@pytest.mark.negative
@pytest.mark.flaky_regression
def test_smoke_invalid_param_returns_400(helper_asteroid, faker_fixture):
    """
    Smoke test: Ensure invalid query param returns HTTP 400 and error message.
    """
    fake_param = faker_fixture.first_name()
    pytest.logger.info(f"Sending request with invalid parameter: fakeparam={fake_param}")

    result = helper_asteroid.fetch_data(
        expected_status_code=HTTPStatusCodes.BAD_REQUEST.value,
        fakeparam=fake_param
    )

    if ResponseKeys.MESSAGE.value not in result:
        pytest.logger.error("Expected error message not found in 400 response.")

    assert ResponseKeys.MESSAGE.value in result
    pytest.logger.info("Proper error message returned for invalid param.")


@pytest.mark.smoke
@pytest.mark.validation
@pytest.mark.flaky_regression
def test_response_schema(helper_asteroid):
    """Validate overall response schema using JSON schema validation."""
    schema = ASTEROID_API_SCHEMA
    pytest.logger.info("Validating response against schema...")

    result = helper_asteroid.fetch_data()
    try:
        validate(instance=result, schema=schema)
        pytest.logger.info("Schema validation passed.")
    except ValidationError as e:
        pytest.logger.error(f"Schema validation failed: {e}")
        pytest.fail(f"Schema validation failed: {e}")


@pytest.mark.flaky_regression
@pytest.mark.negative
@pytest.mark.parametrize("label, param, expected_error", INVALID_PARAMS)
def test_invalid_param(helper_asteroid, label, param, expected_error):
    """Check that invalid parameters return proper error messages."""
    pytest.logger.info(f"[{label}] Sending request with invalid param(s): {param}")

    result = helper_asteroid.fetch_data(expected_status_code=HTTPStatusCodes.BAD_REQUEST.value, **param)
    message = result.get("message", "")

    if expected_error not in message:
        pytest.logger.error(
            f"[{label}] Expected error message not found.\nExpected: '{expected_error}'\nActual: '{message}'"
        )

    assert expected_error in message
    pytest.logger.info(f"[{label}] Invalid param correctly returned expected error message.")


@pytest.mark.flaky_regression
@pytest.mark.edgecase
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_edge_case_no_data(helper_asteroid, label, start, end):
    """Confirm API returns zero results for extreme future date range."""
    pytest.logger.info(f"Testing future range with no data: {start} → {end}")
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value)
    if count != 0:
        pytest.logger.warning(f"Expected 0 results, got {count}")
    assert count == 0


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


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, dist", DISTANCES)
def test_filter_by_distance(helper_asteroid, label, dist):
    """Ensure distance filter reduces or limits result set."""
    pytest.logger.info(f"[{label}] Testing with dist-max={dist} AU")

    params = AsteroidRequestBuilder().with_dist_max(dist).build()
    result = helper_asteroid.fetch_data(**params)

    if ResponseKeys.DATA.value not in result:
        pytest.logger.error(f"[{label}] Response missing '{ResponseKeys.DATA.value}' key")
    else:
        data = result[ResponseKeys.DATA.value]
        if not data:
            pytest.logger.warning(f"[{label}] No results returned for dist-max={dist}")
        else:
            pytest.logger.info(f"[{label}] Retrieved {len(data)} entries within {dist} AU")

    assert ResponseKeys.DATA.value in result


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_results_sorted_by_close_approach_date(helper_asteroid, label, start, end):
    """Check that results are sorted by close-approach date ascending."""
    pytest.logger.info(f"[{label}] Verifying sorting from {start} to {end}")
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    dates = [entry[AsteroidDataFields.CD] for entry in result.get(ResponseKeys.DATA.value, [])]
    parsed_dates = [datetime.strptime(date, NASA_CLOSE_APPROACH_DATE_FORMAT) for date in dates]

    if parsed_dates != sorted(parsed_dates):
        pytest.logger.error(f"[{label}] Dates are not sorted correctly!")

    assert parsed_dates == sorted(parsed_dates)


@pytest.mark.edgecase
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", EMPTY_DATE_RANGES)
def test_empty_ranges_return_no_data(helper_asteroid, label, start, end):
    """Verify empty data sets return zero count and no data array."""
    pytest.logger.info(f"[{label}] Testing with empty date range: {start} → {end}")

    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    count = result.get(ResponseKeys.COUNT.value, 0)
    data = result.get(ResponseKeys.DATA.value, [])

    if count != 0:
        pytest.logger.warning(f"[{label}] Expected count=0, got {count}")
    if data:
        pytest.logger.warning(f"[{label}] Expected no data, but got: {len(data)} items")

    assert count == 0
    assert not data

    pytest.logger.info(f"[{label}] Correctly returned no results for empty range.")


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, dist", COMBINED_DATA_AND_DISTANCE)
def test_combined_date_and_distance_filter(helper_asteroid, label, start, end, dist):
    """Test combined filtering with both date range and maximum distance."""
    pytest.logger.info(f"[{label}] Combined filter: {start} → {end} with dist-max={dist}")
    params = (
        AsteroidRequestBuilder()
        .with_date_range(start, end)
        .with_dist_max(dist)
        .build()
    )

    result = helper_asteroid.fetch_data(**params)
    data = result.get(ResponseKeys.DATA.value, [])

    pytest.logger.debug(f"[{label}] Total entries returned: {len(data)}")
    if not data:
        pytest.logger.warning(f"[{label}] No entries returned with combined filters")

    max_dist = float(dist)
    for i, entry in enumerate(data):
        try:
            approach_distance = float(entry[AsteroidDataFields.DIST])
        except (ValueError, IndexError) as e:
            pytest.logger.error(f"[{label}] Invalid distance at row {i}: {e}")
            pytest.fail(f"Invalid distance value at row {i}: {entry} ({e})")

        assert approach_distance <= max_dist, (
            f"Entry {i} exceeds max distance: {approach_distance} > {max_dist} (entry: {entry})"
        )


@pytest.mark.load
@pytest.mark.flaky_regression
# @pytest.mark.skip(reason="Intentional overloading of the API")
def test_simulate_rate_limit(helper_asteroid, helper_thread):
    """Simulate API 503 by rapid fire calls (skipped by default)."""

    pytest.logger.info("Triggering parallel requests to simulate rate limit...")
    successes, failures, others = helper_thread.simulate_asteroid_load(
        controller=helper_asteroid.controller,
        expected_success=HTTPStatusCodes.OK.value,
        expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value
    )

    pytest.logger.info(
        f"[Threaded Rate Limit] {successes} successful | {failures} failed (503s) | {others} other"
    )

    if failures == 0:
        pytest.logger.warning("Expected at least one 503 but none occurred.")

    assert failures >= 1, (
        f"Expected at least one {HTTPStatusCodes.SERVICE_UNAVAILABLE.value} error under load"
    )
