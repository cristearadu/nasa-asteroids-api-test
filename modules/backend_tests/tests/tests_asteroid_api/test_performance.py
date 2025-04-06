import pytest

from core import HTTPStatusCodes


@pytest.mark.performance
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
