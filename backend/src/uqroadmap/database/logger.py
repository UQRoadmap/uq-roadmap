"""Logging setup."""

import logging

from uqroadmap.config import CONFIG

LOG_FORMAT = "%(asctime)s %(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging() -> None:
    """Setting up the logging."""
    log_level_val = CONFIG.log_level.get_level()

    logger = logging.getLogger("csse3200bot")
    logger.setLevel(log_level_val)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_val)

    file_handler = logging.FileHandler("discord-bots.log", encoding="utf-8", mode="w")
    file_handler.setLevel(log_level_val)

    # Set Formatters
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
