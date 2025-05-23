import pytest
import logging
import os
import http.client as http_client
from faker import Faker
from datetime import datetime
from core import ROOT_WORKING_DIRECTORY, LOGS_FOLDER
from modules.backend_tests import HelperAsteroidData, HelperThread


def pytest_configure(config):
    """
    pytest.logger.debug("This is a DEBUG message")       # Show in console, NOT in files
    pytest.logger.info("This is an INFO message")
    pytest.logger.warning("This is a WARNING message")
    pytest.logger.error("This is an ERROR message")
    pytest.logger.critical("This is a CRITICAL message")
    """
    # enable HTTP connection logging
    http_client.HTTPConnection.debuglevel = 0  # Set to 1 for full request/response dumps

    # Create the log folder if it doesn't exist
    log_dir = os.path.join(ROOT_WORKING_DIRECTORY, LOGS_FOLDER)
    os.makedirs(log_dir, exist_ok=True)

    if not os.environ.get("PYTEST_LOG_FILE"):
        timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
        log_file = os.path.join(log_dir, f"{timestamp}.log")
        os.environ["PYTEST_LOG_FILE"] = log_file  # store in env variable
    else:
        log_file = os.environ["PYTEST_LOG_FILE"]  # all the other workers use the same file

    logger = logging.getLogger("pytest-logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        for ext_logger_name in ["urllib3", "requests", "http.client"]:
            ext_logger = logging.getLogger(ext_logger_name)
            ext_logger.setLevel(logging.DEBUG)
            ext_logger.addHandler(file_handler)
            ext_logger.propagate = False  # Avoid double logging

    pytest.logger = logger

    # register a custom marker: flaky + regression
    config.addinivalue_line("markers", "flaky_regression: Combines regression + flaky retry for unstable tests")
    setattr(pytest.mark, "flaky_regression",
            pytest.mark.regression(pytest.mark.flaky(reruns=3, reruns_delay=1)))


def pytest_runtest_call(item):
    """
    Hook to log test docstrings before execution.
    """
    test_docstring = item.function.__doc__
    if test_docstring:
        pytest.logger.info(f"\nRunning Test: {item.name}\n{test_docstring.strip()}\n")


def pytest_collection_modifyitems(session, config, items):
    """
    Ensures that smoke tests run first in any test run.
    """
    smoke_tests = [item for item in items if "smoke" in item.keywords]
    other_tests = [item for item in items if "smoke" not in item.keywords]

    # Reorder items: smoke tests first
    items[:] = smoke_tests + other_tests


@pytest.fixture
def helper_asteroid():
    return HelperAsteroidData()


@pytest.fixture
def helper_thread():
    return HelperThread(threads=20)


@pytest.fixture
def faker_fixture():
    return Faker()
