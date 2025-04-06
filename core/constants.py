import os
from enum import Enum, IntEnum


ROOT_WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FOLDER = 'output'
NASA_CLOSE_APPROACH_DATE_FORMAT = "%Y-%b-%d %H:%M"


class HTTPStatusCodes(Enum):
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ResponseKeys(Enum):
    COUNT = "count"
    DATA = "data"
    MESSAGE = "message"
    SIGNATURE = "signature"


class AsteroidDataFields(IntEnum):
    DES = 0         # Designation
    ORB = 1         # Orbit ID
    JD = 2               # Julian Date
    CD = 3               # Close-Approach Date (formatted)
    DIST = 4             # Nominal approach distance (au)
    DIST_MIN = 5         # Minimum possible distance (au)
    DIST_MAX = 6         # Maximum possible distance (au)
    V_REL = 7            # Relative velocity (km/s)
    V_INF = 8            # Velocity relative to Earth (km/s)
    T_SIGMA_F = 9        # Time uncertainty
    H = 10               # Absolute magnitude
    DIAMETER = 11        # Estimated diameter (may be None)
    DIAMETER_SIGMA = 12  # Uncertainty in diameter


class KindValues(str, Enum):
    ASTEROID = "a"
    COMET = "c"
    PLANET = "p"  # currently unsupported, returns 400


ASTEROID_API_SCHEMA = {
    "type": "object",
    "properties": {
        ResponseKeys.COUNT.value: {"type": "integer"},
        ResponseKeys.DATA.value: {"type": "array"},
        ResponseKeys.SIGNATURE.value: {"type": "object"},
    },
    "required": [ResponseKeys.COUNT.value, ResponseKeys.SIGNATURE.value]
}

# Pattern to match fullname field, e.g., '       (2024 AV2)' or '(433 Eros)'
FULLNAME_REGEX_PATTERN = r".*(\([^\)]+\))?$"
