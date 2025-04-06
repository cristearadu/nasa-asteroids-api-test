import pytest

from modules.backend_tests import AsteroidRequestBuilder, VALID_SORTING_DATES
from core import ResponseKeys, AsteroidDataFields, NASA_CLOSE_APPROACH_DATE_FORMAT, DATE_FORMAT_ISO
from datetime import datetime


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


@pytest.mark.flaky_regression
@pytest.mark.validation
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_close_approach_date_format_is_valid(helper_asteroid, label, start, end):
    """Validate all close-approach dates conform to the expected NASA format."""
    pytest.logger.info(f"[{label}] Validating 'cd' format for entries between {start} and {end}")
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    for entry in result.get(ResponseKeys.DATA.value, []):
        date_str = entry[AsteroidDataFields.CD]
        try:
            datetime.strptime(date_str, NASA_CLOSE_APPROACH_DATE_FORMAT)
        except ValueError:
            pytest.fail(f"[{label}] Invalid {AsteroidDataFields.CD.name} format: {date_str}")


@pytest.mark.validation
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_cd_field_is_present_and_not_empty(helper_asteroid, label, start, end):
    """Ensure all entries contain a non-empty 'cd' (close-approach date)."""
    pytest.logger.info(f"[{label}] Checking non-empty 'cd' field from {start} to {end}")
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    for entry in result.get(ResponseKeys.DATA.value, []):
        cd_value = entry[AsteroidDataFields.CD]
        assert cd_value, f"'{AsteroidDataFields.CD.name}' field is empty or null in entry: {entry}"


@pytest.mark.validation
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end", VALID_SORTING_DATES)
def test_cd_within_requested_date_range(helper_asteroid, label, start, end):
    """Ensure 'cd' values fall within the specified date range."""
    pytest.logger.info(f"[{label}] Verifying 'cd' is within {start} to {end}")
    params = AsteroidRequestBuilder().with_date_range(start, end).build()
    result = helper_asteroid.fetch_data(**params)

    start_date = datetime.strptime(start, DATE_FORMAT_ISO)
    end_date = datetime.strptime(end, DATE_FORMAT_ISO)

    for entry in result.get(ResponseKeys.DATA.value, []):
        cd_date = datetime.strptime(entry[AsteroidDataFields.CD], NASA_CLOSE_APPROACH_DATE_FORMAT)
        assert start_date <= cd_date <= end_date, f"'{AsteroidDataFields.CD.name}' out of range: {cd_date}"


@pytest.mark.validation
@pytest.mark.smoke
def test_cd_values_are_unique(helper_asteroid):
    """Ensure 'cd' values are not duplicated in the response (optional)."""
    result = helper_asteroid.fetch_data()
    cd_values = [entry[AsteroidDataFields.CD] for entry in result.get(ResponseKeys.DATA.value, [])]
    assert len(cd_values) == len(set(cd_values)), "Duplicate '{AsteroidDataFields.CD.name}' values detected"
