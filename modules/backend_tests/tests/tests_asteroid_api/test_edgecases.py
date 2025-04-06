import pytest

from core import ResponseKeys
from modules.backend_tests import AsteroidRequestBuilder
from modules.backend_tests.tests.tests_asteroid_api.test_data import EMPTY_DATE_RANGES


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
