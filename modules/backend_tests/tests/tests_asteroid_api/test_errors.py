import pytest

from core import HTTPStatusCodes, ResponseKeys
from modules.backend_tests.tests.tests_asteroid_api.test_data import INVALID_PARAMS


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


@pytest.mark.flaky_regression
@pytest.mark.negativedocker
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
