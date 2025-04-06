from core import get_request


class AsteroidAPIController:
    BASE_URL = "https://ssd-api.jpl.nasa.gov/cad.api"

    def get_close_approach_data(self, params):
        return get_request(url=self.BASE_URL, params=params if params else {})
