import pytest

from modules.backend_tests import AsteroidRequestBuilder
from modules.backend_tests.helpers.helper_asteroids_data import HelperAsteroidData
from modules.backend_tests.tests.tests_asteroid_api.test_data import BOUNDARY_TEST_CASES
from core import ResponseKeys


@pytest.mark.validation
@pytest.mark.edgecase
@pytest.mark.flaky_regression
@pytest.mark.parametrize("label, param_key, value, field_index, condition_fn", BOUNDARY_TEST_CASES)
def test_boundary_conditions(helper_asteroid: HelperAsteroidData, label, param_key, value, field_index, condition_fn):
    """Parameterized test for validating API boundary conditions."""
    pytest.logger.info(f"[{label}] Testing {param_key}={value}")

    builder = AsteroidRequestBuilder()
    method = getattr(builder, f"with_{param_key.replace('-', '_')}")
    params = method(value).build() if value is not None else method().build()

    result = helper_asteroid.fetch_data(**params)
    data = result.get(ResponseKeys.DATA.value, [])
    pytest.logger.debug(f"[{label}] Received {len(data)} results")

    if not data:
        pytest.logger.warning(f"[{label}] No data returned for {param_key}={value}")
    else:
        assert all(condition_fn(entry[field_index]) for entry in data), \
            f"[{label}] One or more entries failed validation"
