"""Course models."""

from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import BaseDBModel
from common.enums import CourseLevel, CourseMode, CourseSemester


class CourseSecatQuestionsDBModel(BaseDBModel):
    """DB Model for secat questions."""

    __tablename__ = "course_secat_quesions"

    question_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    secat_id: Mapped[UUID] = mapped_column(ForeignKey("course_secat.secat_id"))

    name: Mapped[str]
    s_agree: Mapped[float]
    agree: Mapped[float]
    middle: Mapped[float]
    disagree: Mapped[float]
    s_disagree: Mapped[float]


class CourseSecatDBModel(BaseDBModel):
    """DB Model for secats."""

    __tablename__ = "course_secat"

    __table_args__ = (UniqueConstraint("course_id"),)  # we're only have 1 secat per course for now

    secat_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("course.course_id"))

    num_enrolled: Mapped[int]
    num_responses: Mapped[int]
    response_rate: Mapped[float]

    questions: Mapped[list[CourseSecatQuestionsDBModel]] = relationship(
        CourseSecatQuestionsDBModel,
        cascade="all, delete-orphan",
        lazy="joined",  # we always want the questions with it
    )


class CourseOfferingDBModel(BaseDBModel):
    """DB Model for Course offerings."""

    __tablename__ = "course_offering"

    offering_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("course.course_id"))

    year: Mapped[int]
    semester: Mapped[str]
    mode: Mapped[CourseMode]

    location: Mapped[str]
    profile_url: Mapped[str | None]
    active: Mapped[bool]

    @hybrid_property
    def semester_enum(self) -> CourseSemester:
        """Get full course code e.g., 'CSSE1001."""
        start = self.semester.split(",")[0]

        try:
            return CourseSemester(start)
        except ValueError:
            return CourseSemester.OTHER


class CourseDBModel(BaseDBModel):
    """DB Model for a course."""

    __tablename__ = "course"

    __table_args__ = (UniqueConstraint("category", "code"),)

    course_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # another candidate
    category: Mapped[str]
    code: Mapped[str]

    # info
    name: Mapped[str]
    description: Mapped[str]
    level: Mapped[CourseLevel]
    num_units: Mapped[float]
    incompatible: Mapped[dict | None] = mapped_column(JSON)
    prerequisite: Mapped[dict | None] = mapped_column(JSON)

    active: Mapped[bool]
    semesters_str: Mapped[str | None]  # comma seperated version of enums

    # Misc Info
    attendance_mode: Mapped[CourseMode]
    faculty: Mapped[str]
    faculty_url: Mapped[str | None]
    school: Mapped[str]
    duration: Mapped[int]
    class_hours: Mapped[str | None]
    course_enquries: Mapped[str | None]

    # Offerings
    offerings: Mapped[list[CourseOfferingDBModel]] = relationship(CourseOfferingDBModel, cascade="all, delete-orphan")

    secat: Mapped[CourseSecatDBModel | None] = relationship(
        CourseSecatDBModel, cascade="all, delete-orphan", lazy="joined"
    )

    assessment: Mapped[dict | None] = mapped_column(JSON)

    @hybrid_property
    def full_code(self) -> str:
        """Get full course code e.g., 'CSSE1001."""
        return self.category + self.code
