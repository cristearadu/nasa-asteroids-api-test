import pytest

from modules.backend_tests import AsteroidRequestBuilder
from core import ResponseKeys, KindValues
from modules.backend_tests.tests.tests_asteroid_api.test_data import (
    DATE_RANGES
)


@pytest.mark.negative
@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, _", DATE_RANGES[:1])  # Use one valid range for simplicity
def test_filter_only_planets(helper_asteroid, label, start, end, _):
    """Verify that filtering with kind=p (planets) returns a 400 as it's not supported."""
    pytest.logger.warning(f"[{label}] Expecting 400 for kind=p with date range {start} to {end}")
    params = (
        AsteroidRequestBuilder()
        .with_kind(KindValues.PLANET.value)
        .with_date_range(start, end)
        .build()
    )
    result = helper_asteroid.fetch_data(expected_status_code=400, **params)
    assert "invalid" in result.get("message", "").lower()


@pytest.mark.filtering
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, start, end, _", DATE_RANGES[:1])
def test_filter_only_comets(helper_asteroid, label, start, end, _):
    """Filter to include only comets using kind=c with a valid date range."""
    pytest.logger.info(f"[{label}] Filtering by kind=c and date range {start} to {end}")
    params = (
        AsteroidRequestBuilder()
        .with_kind(KindValues.COMET.value)
        .with_date_range(start, end)
        .build()
    )
    result = helper_asteroid.fetch_data(**params)

    assert ResponseKeys.COUNT.value in result
    if result[ResponseKeys.COUNT.value] > 0:
        assert ResponseKeys.DATA.value in result
        for entry in result[ResponseKeys.DATA.value]:
            assert entry  # basic existence check
    else:
        pytest.logger.info("No comets found in selected date range, as expected.")


@pytest.mark.negative
@pytest.mark.flaky_regression
def test_invalid_kind_value_returns_400(helper_asteroid, faker_fixture):
    """Send invalid kind param and expect HTTP 400."""
    fake_param = faker_fixture.first_name()
    params = {"kind": fake_param}
    pytest.logger.warning(f"Sending invalid {params}")
    result = helper_asteroid.fetch_data(expected_status_code=400, **params)
    message = result.get("message", "").lower()
    assert "invalid object kind" in message
