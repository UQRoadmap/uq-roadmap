"""Course models."""

from common.enums import CourseLevel
from common.schemas import AssessmentItem, SecatInfo, UQRoadmapBase


class ScrapedCourseOffering(UQRoadmapBase):
    """Course offering."""

    semester: str
    location: str
    mode: str
    profile_url: str | None = None


class ScrapedCourse(UQRoadmapBase):
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

    latest_assessment: list[AssessmentItem] | None = None

    secat: SecatInfo | None = None

    # Offerings
    current_offerings: list[ScrapedCourseOffering]
    archived_offerings: list[ScrapedCourseOffering]

    @property
    def code_parts(self) -> tuple[str, str]:
        """Split the course code up (e.g., CSSE2310 -> "CSSE", "2310")."""
        for i, ch in enumerate(self.code):
            if ch.isdigit():
                return self.code[:i], self.code[i:]
        return self.code, ""
