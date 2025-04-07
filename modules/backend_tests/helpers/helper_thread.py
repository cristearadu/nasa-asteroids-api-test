from concurrent.futures import ThreadPoolExecutor, as_completed
from core import HTTPStatusCodes
import pytest


class HelperThread:
    """
    Utility class to simulate concurrent load on the Asteroids API using threading.
    """
    def __init__(self, threads=20):
        self.threads = threads

    def simulate_parallel_requests(
        self,
        request_fn,
        expected_success=HTTPStatusCodes.OK.value,
        expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value
    ):
        """
        Executes the provided request function in parallel across multiple threads.

        Args:
            request_fn (Callable): The function to call in each thread. Must return a status code.
            expected_success (int): Expected HTTP status code for a successful request.
            expected_failure (int): Expected HTTP status code for a failed (rate-limited) request.

        Returns:
            Tuple[int, int, int]: A count of (successes, failures, unexpected responses).
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

    def simulate_asteroid_load(self, controller, expected_success=HTTPStatusCodes.OK.value,
                               expected_failure=HTTPStatusCodes.SERVICE_UNAVAILABLE.value):
        """
        Convenience method to simulate load against the Asteroids API using default parameters.

        Args:
            controller: An instance with `get_close_approach_data()` method.
            expected_success (int): Expected HTTP 200 OK response code.
            expected_failure (int): Expected HTTP 503 rate-limited response code.

        Returns:
            Tuple[int, int, int]: A count of (successes, failures, unexpected responses).
        """

        def make_call():
            response = controller.get_close_approach_data({})
            return response.status_code

        return self.simulate_parallel_requests(
            request_fn=make_call,
            expected_success=expected_success,
            expected_failure=expected_failure
        )
