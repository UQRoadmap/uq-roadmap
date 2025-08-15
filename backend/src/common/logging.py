"""Logging setup."""

import logging

from common.enums import LogLevel

LOG_FORMAT = "%(asctime)s %(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging(level: LogLevel) -> None:
    """Setting up the logging."""
    log_level_val = level.get_level()

    logger = logging.getLogger("uqroadmap")
    logger.setLevel(log_level_val)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_val)

    # Set Formatters
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
