"""Course models."""

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import BaseDBModel
from common.enums import CourseLevel, CourseOfferingMode, UniversitySemester


class CourseSecatQuestionsDBModel(BaseDBModel):
    """DB Model for secat questions."""

    __tablename__ = "course_secat_quesions"

    secat_id: Mapped[UUID] = mapped_column(ForeignKey("course_secat.secat_id"), primary_key=True)

    name: Mapped[str]
    s_agree: Mapped[float]
    agree: Mapped[float]
    middle: Mapped[float]
    disagree: Mapped[float]
    s_disagree: Mapped[float]


class CourseSecatDBModel(BaseDBModel):
    """DB Model for secats."""

    __tablename__ = "course_secat"

    __table_args__ = (
        UniqueConstraint("course_category", "course_code"),
        ForeignKeyConstraint(["course_category", "course_code"], ["course.category", "course.code"]),
    )  # we're only have 1 secat per course for now

    secat_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    course_category: Mapped[str] = mapped_column()
    course_code: Mapped[str] = mapped_column()

    questions: Mapped[list[CourseSecatQuestionsDBModel]] = relationship(
        CourseSecatQuestionsDBModel,
        cascade="all, delete-orphan",
        lazy="joined",  # we always want the questions with it
    )


class CourseOfferingDBModel(BaseDBModel):
    """DB Model for Course offerings."""

    __tablename__ = "course_offering"

    __table_args__ = (ForeignKeyConstraint(["course_category", "course_code"], ["course.category", "course.code"]),)

    course_category: Mapped[str] = mapped_column(primary_key=True)
    course_code: Mapped[str] = mapped_column(primary_key=True)

    year: Mapped[int]
    semester: Mapped[UniversitySemester]
    location: Mapped[str]
    mode: Mapped[CourseOfferingMode]
    profile_url: Mapped[str | None]
    active: Mapped[bool]


class CourseDBModel(BaseDBModel):
    """DB Model for a course."""

    __tablename__ = "course"

    # General info
    category: Mapped[str] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    level: Mapped[CourseLevel]
    num_units: Mapped[float]
    incompatible: Mapped[str | None]
    prerequisite: Mapped[str | None]

    # Misc Info
    faculty: Mapped[str]
    faculty_url: Mapped[str | None]
    school: Mapped[str]
    duration: Mapped[int]
    class_hours: Mapped[str | None]
    course_enquries: Mapped[str | None]

    # Offerings
    offerings: Mapped[list[CourseOfferingDBModel]] = relationship(CourseOfferingDBModel, cascade="all, delete-orphan")

    @hybrid_property
    def full_code(self) -> str:
        """Get full course code e.g., 'CSSE1001."""
        return self.category + self.code

    @hybrid_property
    def active(self) -> bool:
        """Get full course code e.g., 'CSSE1001."""
        return bool([])
