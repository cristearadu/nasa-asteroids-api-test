import os
from enum import Enum, IntEnum
from typing import Optional, Union
from pydantic import BaseModel

ROOT_WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FOLDER = 'output'
NASA_CLOSE_APPROACH_DATE_FORMAT = "%Y-%b-%d %H:%M"
DATE_FORMAT_ISO = "%Y-%m-%d"


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
    DES = 0              # Designation
    ORB = 1              # Orbit ID
    JD = 2               # Julian Date
    CD = 3               # Close-Approach Date (formatted)
    DIST = 4             # Nominal approach distance (au)
    DIST_MIN = 5         # Minimum possible distance (au)
    DIST_MAX = 6         # Maximum possible distance (au)
    V_REL = 7            # Relative velocity (km/s)
    V_INF = 8            # Velocity-infinity (km/s)
    T_SIGMA_F = 9        # Time uncertainty
    H = 10               # Absolute magnitude
    DIAMETER = 11        # Estimated diameter (if requested)
    DIAMETER_SIGMA = 12  # Uncertainty in diameter estimate


class KindValues(str, Enum):
    ASTEROID = "a"
    COMET = "c"
    PLANET = "p"  # currently unsupported, returns 400


ASTEROID_API_SCHEMA = {
    "type": "object",
    "required": [
        ResponseKeys.COUNT.value,
        ResponseKeys.DATA.value,
        ResponseKeys.SIGNATURE.value
    ],
    "properties": {
        ResponseKeys.COUNT.value: {"type": "integer"},
        ResponseKeys.DATA.value: {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "number"},
                        {"type": "null"}
                    ]
                }
            }
        },
        ResponseKeys.SIGNATURE.value: {
            "type": "object",
            "required": ["version", "source"],
            "properties": {
                "version": {"type": "string"},
                "source": {"type": "string"}
            }
        }
    }
}


class CadEntry(BaseModel):
    des: str
    orbit_id: str
    jd: Union[str, float]
    cd: str
    dist: str
    dist_min: str
    dist_max: str
    v_rel: str
    v_inf: str
    t_sigma_f: str
    h: str
    diameter: Optional[float] = None
    diameter_sigma: Optional[float] = None


# Pattern to match fullname field, e.g., '       (2024 AV2)' or '(433 Eros)'
FULLNAME_REGEX_PATTERN = r".*(\([^\)]+\))?$"
