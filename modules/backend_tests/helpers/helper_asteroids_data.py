from modules.backend_tests.controllers.asteroid_api_controller import AsteroidAPIController
from core.constants import HTTPStatusCodes


class HelperAsteroidData:
    def __init__(self):
        self.controller = AsteroidAPIController()

    def fetch_data(self, expected_status_code=HTTPStatusCodes.OK.value, **params):
        response = self.controller.get_close_approach_data(params)
        assert response.status_code == expected_status_code, (f"Expected: {expected_status_code}, "
                                                              f"actual response: {response.status_code}")
        return response.json()
