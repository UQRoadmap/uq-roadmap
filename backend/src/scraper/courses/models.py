"""Course models."""

from pydantic import computed_field

from common.enums import CourseLevel
from scraper.models import UQScrapeModel


class ScrapedCourseOffering(UQScrapeModel):
    """Course offering."""

    semester: str
    location: str
    mode: str
    profile_url: str | None = None


class ScrapedSecatQuestion(UQScrapeModel):
    """Secat question."""

    name: str
    s_agree: float
    agree: float
    middle: float
    disagree: float
    s_disagree: float


class ScrapedSecatInfo(UQScrapeModel):
    """Secat information for a course."""

    num_enrolled: int
    num_responses: int
    response_rate: float
    questions: list[ScrapedSecatQuestion]


class ScrapedAssessment(UQScrapeModel):
    """Scraped assessment info."""

    task: str
    category: str | None = None
    description: str | None = None
    weight: float | None = None
    due_date: str | None = None
    mode: str | None = None
    learning_outcomes: list[str]

    # Flags
    hurdle: bool
    identity_verified: bool


class ScrapedCourse(UQScrapeModel):
    """Course data model."""

    # General info
    code: str
    name: str
    description: str
    level: CourseLevel
    num_units: float
    incompatible: str | None = None
    prerequisite: str | None = None

    # Misc Info
    faculty: str
    faculty_url: str | None = None
    school: str
    duration: int
    attendance_mode: str
    class_hours: str | None = None
    course_enquries: str | None = None

    latest_assessment: list[ScrapedAssessment] | None = None

    secat: ScrapedSecatInfo | None = None

    # Offerings
    current_offerings: list[ScrapedCourseOffering]
    archived_offerings: list[ScrapedCourseOffering]

    @property
    @computed_field
    def active(self) -> bool:
        """Whether the course is active or not."""
        return bool(self.current_offerings)
