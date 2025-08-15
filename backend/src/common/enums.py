"""Enums module."""

import logging
from enum import Enum


class LogLevel(str, Enum):
    """Log levels."""

    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"

    def get_level(self) -> int:
        """Map the log level enum to the logging module level."""
        mapping: dict[LogLevel, int] = {
            LogLevel.info: logging.INFO,
            LogLevel.warn: logging.WARNING,
            LogLevel.error: logging.ERROR,
            LogLevel.debug: logging.DEBUG,
        }
        return mapping[self]
