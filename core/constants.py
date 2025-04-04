import os
from enum import Enum


ROOT_WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FOLDER = 'output'


class HTTPStatusCodes(Enum):
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class ResponseKeys(Enum):
    COUNT = "count"
    DATA = "data"
    MESSAGE = "message"
    SIGNATURE = "signature"
