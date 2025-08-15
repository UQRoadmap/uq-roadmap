"""App config module."""

from pydantic import Field
from pydantic_settings import BaseSettings

from common.enums import LogLevel


class GeneralSettings(BaseSettings):
    """General app settings."""

    db_url: str = Field()
    log_level: LogLevel = Field(default=LogLevel.debug)


CONFIG = GeneralSettings()  # type: ignore[call-arg]
