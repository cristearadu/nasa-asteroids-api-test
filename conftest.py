import pytest
import logging
import os
from datetime import datetime
from core.constants import ROOT_WORKING_DIRECTORY, LOGS_FOLDER
from modules.backend_tests.helpers.helper_asteroids_data import HelperAsteroidData


def pytest_configure():
    """
    pytest.logger.debug("This is a DEBUG message")       # Show in console, NOT in files
    pytest.logger.info("This is an INFO message")
    pytest.logger.warning("This is a WARNING message")
    pytest.logger.error("This is an ERROR message")
    pytest.logger.critical("This is a CRITICAL message")
    """
    log_dir = os.path.join(ROOT_WORKING_DIRECTORY, LOGS_FOLDER)
    os.makedirs(log_dir, exist_ok=True)

    # if no log file is set -> generate a new one for the first worker
    if not os.environ.get("PYTEST_LOG_FILE"):
        timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
        log_file = os.path.join(log_dir, f"{timestamp}.log")
        os.environ["PYTEST_LOG_FILE"] = log_file  # store in env variable
    else:
        log_file = os.environ["PYTEST_LOG_FILE"]  # all the other workers use the same file

    logger = logging.getLogger("pytest-logger")
    logger.setLevel(logging.DEBUG)

    # just prevent duplicate handlers
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

    pytest.logger = logger


def pytest_runtest_call(item):
    """
    Hook to log test docstrings before execution.
    """
    test_docstring = item.function.__doc__
    if test_docstring:
        pytest.logger.info(f"\nRunning Test: {item.name}\n{test_docstring.strip()}\n")


@pytest.fixture
def asteroid_helper():
    return HelperAsteroidData()
