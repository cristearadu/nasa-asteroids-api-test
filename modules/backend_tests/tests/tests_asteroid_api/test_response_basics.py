import pytest

from modules.backend_tests.tests.tests_asteroid_api.test_data import *
from modules.backend_tests import AsteroidRequestBuilder
from core import ResponseKeys, AsteroidDataFields, NASA_CLOSE_APPROACH_DATE_FORMAT
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


