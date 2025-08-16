"""Logging setup."""

import logging

from common.enums import LogLevel

LOG_FORMAT = "%(asctime)s %(levelname)s:%(message)s:%(funcName)s:%(lineno)d"


def configure_logging(level: LogLevel) -> None:
    """Setting up the logging."""
    log_level_val = level.get_level()

    logging.basicConfig(level=log_level_val, format=LOG_FORMAT)
