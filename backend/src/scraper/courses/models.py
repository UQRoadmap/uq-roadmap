"""Course models."""

from pydantic import computed_field

from common.enums import CourseLevel
from scraper.models import UQScrapeModel


class CourseOffering(UQScrapeModel):
    """Course offering."""

    semester: str
    location: str
    mode: str
    profile_url: str | None


class SecatQuestion(UQScrapeModel):
    """Secat question."""

    name: str
    s_agree: float
    agree: float
    middle: float
    disagree: float
    s_disagree: float


class CourseSecatInfo(UQScrapeModel):
    """Secat information for a course."""

    num_enrolled: int
    num_responses: int
    response_rate: float
    questions: list[SecatQuestion]


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
    faculty_url: str | None
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
