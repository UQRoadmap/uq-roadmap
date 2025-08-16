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


class CourseSemester(StrEnum):
    """University Semesters."""

    RQ1 = "Research Quarter 1"
    RQ2 = "Research Quarter 2"
    RQ3 = "Research Quarter 3"
    RQ4 = "Research Quarter 4"
    SFC = "SFC Enrolment Year"
    SEM1 = "Semester 1"
    SEM2 = "Semester 2"
    SUM_SEM = "Summer Semester"
    TRIM_1 = "Trimester 1"
    TRIM_2 = "Trimester 2"
    TRIM_3 = "Trimester 3"
    COLLEGE1 = "UQ College Intake 1"
    COLLEGE2 = "UQ College Intake 2"
    OTHER = "Other"


class CourseMode(StrEnum):
    """Course offering mode."""

    WORK_EXPERIENCE = "Work Experience"
    IN_PERSON = "In Person"
    EXTERNAL = "External"
    INTERNAL = "Internal"
    WEEKEND = "Weekend"
    JULY_INTENSIVE = "July Intensive"
    OFFSHORE = "Off-Shore"
    OFF_CAMPUS = "Off-Campus"
    INTENSIVE = "Intensive"
    WEB_BASED = "Web Based"
    REMOTE = "Remote"
    FLEXIBLE = "Flexible Delivery"
