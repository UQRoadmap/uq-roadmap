"""Enums module."""

import logging
from enum import Enum, StrEnum


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


class CourseLevel(StrEnum):
    """Level of a course."""

    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    POSTGRADUATE_COURSEWORK = "postgraduate coursework"
    UQ_COLLEGE = "uq college"
    NON_AWARD = "non-award"
    OTHER = "other"


class UniversitySemester(StrEnum):
    """University Semesters."""

    SEM1 = "Semester 1"
    SEM2 = "Semester 2"
    SSEM = "Summer Semester"
    WSEM = "Winter Semester"


class CourseOfferingMode(StrEnum):
    """Course offering mode."""

    WORK_EXPERIENCE = "Work Experience"
    IN_PERSON = "In Person"
    EXTERNAL = "External"
    WEEKEND = "Weekend"
    JULY_INTENSIVE = "July Intensive"
    OFFSHORE = "Off-Shore"
    OFF_CAMPUS = "Off-Campus"
    INTENSIVE = "Intensive"
    WEB_BASED = "Web Based"
    REMOTE = "Remote"
    FLEXIBLE = "Flexible Delivery"
