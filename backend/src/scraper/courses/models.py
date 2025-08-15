"""Course models."""

from enum import Enum

from pydantic import HttpUrl, computed_field

from scraper.models import UQScrapeModel


class CourseLevel(Enum):
    """Level of a course."""

    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    POSTGRADUATE_COURSEWORK = "postgraduate coursework"
    UQ_COLLEGE = "uq college"
    NON_AWARD = "non-award"
    OTHER = "other"


class CourseOffering(UQScrapeModel):
    """Course offering."""

    semester: str
    location: str
    mode: str
    profile_url: HttpUrl | None


class CourseSecatInfo(UQScrapeModel):
    """Secat information for a course."""

    num_enrolled: int
    num_responses: int
    response_rate: float


class Course(UQScrapeModel):
    """Course data model."""

    # General info
    code: str
    name: str
    description: str
    level: CourseLevel
    num_units: float
    incompatible: str | None
    prerequisite: str | None

    # Misc Info
    faculty: str
    faculty_url: HttpUrl | None
    school: str
    duration: int
    attendance_mode: str
    class_hours: str | None
    course_enquries: str | None

    # Offerings
    current_offerings: list[CourseOffering]
    archived_offerings: list[CourseOffering]

    @property
    @computed_field
    def active(self) -> bool:
        """Whether the course is active or not."""
        return bool(self.current_offerings)
