"""Course schemas."""

from uuid import UUID

from pydantic import computed_field

from common.enums import CourseLevel, CourseMode, CourseSemester
from common.reqs_parsing import RequirementRead
from common.schemas import AssessmentItem, SecatInfo, UQRoadmapBase


class CourseOfferingRead(UQRoadmapBase):
    """Read a course offering."""

    offering_id: UUID
    year: int
    semester: str
    mode: CourseMode
    location: str
    profile_url: str | None
    active: bool
    semester_enum: CourseSemester


class CourseAssessment(UQRoadmapBase):
    """Course Asessment."""

    items: list[AssessmentItem]


class CourseRead(UQRoadmapBase):
    """Read schema for course."""

    course_id: UUID

    # another candidate
    category: str
    code: str

    @computed_field  # type: ignore[misc]
    @property
    def full_code(self) -> str:
        """Get full course code e.g., 'CSSE1001."""
        return self.category + self.code

    name: str
    description: str
    level: CourseLevel
    num_units: float
    attendance_mode: CourseMode

    active: bool  # whether the course is active
    semesters_str: str | None  # comma seperate enum of semesters

    @computed_field  # type: ignore[misc]
    @property
    def semesters(self) -> list[CourseSemester]:
        """Get recent possible semesters of courses."""
        if self.semesters_str is None:
            return []
        return [CourseSemester(s) for s in self.semesters_str.split(",")]

    secat: SecatInfo | None

    @computed_field  # type: ignore[misc]
    @property
    def score(self) -> float | None:
        """Get score out of 100% for course based on secats."""
        return self.secat.get_avg_score() if self.secat else None

    assessment: CourseAssessment | None


class CourseReadDetailed(CourseRead):
    """Detailed read schema for course."""

    offerings: list[CourseOfferingRead]
    incompatible: RequirementRead | None
    prerequisite: RequirementRead | None

    faculty: str
    faculty_url: str | None
    school: str
    duration: int
    class_hours: str | None
    course_enquries: str | None
