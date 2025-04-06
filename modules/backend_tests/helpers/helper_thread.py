from concurrent.futures import ThreadPoolExecutor, as_completed
from core import HTTPStatusCodes
import pytest


class HelperThread:
    def __init__(self, threads=20):
        self.threads = threads

    def simulate_parallel_requests(
        self,
        request_fn,
        expected_success=HTTPStatusCodes.OK.value,
        expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value
    ):
        """
        Runs the given request function concurrently across N threads.
        Returns a tuple: (successes, failures, others)
        """
        successes, failures, others = 0, 0, 0

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(request_fn) for _ in range(self.threads)]

            for future in as_completed(futures):
                try:
                    status_code = future.result()
                    if status_code == expected_failure:
                        failures += 1
                    elif status_code == expected_success:
                        successes += 1
                    else:
                        pytest.logger.warning(f"Unexpected response: {status_code}")
                        others += 1
                except Exception as e:
                    pytest.logger.error(f"Thread call error: {e}")
                    others += 1

        return successes, failures, others

    def simulate_asteroid_load(self, controller, expected_success=200, expected_failure=503):
        """Built-in method for testing asteroid API load."""

        def make_call():
            response = controller.get_close_approach_data({})
            return response.status_code

        return self.simulate_parallel_requests(
            request_fn=make_call,
            expected_success=expected_success,
            expected_failure=expected_failure
        )
