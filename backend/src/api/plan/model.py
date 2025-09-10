"""Plan model."""

from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import BaseDBModel
from api.degree.models import DegreeDBModel


class PlanDBModel(BaseDBModel):
    """DB Model for representing user plans."""

    __tablename__ = "plan"

    plan_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    degree_id: Mapped[UUID] = mapped_column(ForeignKey("degree.degree_id"))
    degree: Mapped[DegreeDBModel] = relationship(DegreeDBModel, lazy="joined")

    name: Mapped[str]
    start_year: Mapped[int]
    start_sem: Mapped[int]
    end_year: Mapped[int]

    # maps (year, sem) -> course_codes e.g., 'CSSE2310"
    course_dates_input: Mapped[dict[str, list[str]]] = mapped_column(JSON)

    # maps (part) -> course_code list
    course_reqs: Mapped[dict[str, list[str]]] = mapped_column(JSON)

    # maps (part) -> degree code (e.g., "2525")
    specialisations: Mapped[dict[str, list[str]]] = mapped_column(JSON)

    @hybrid_property
    def courses(self) -> list[str]:
        """Get full list of course codes (.e.g, "CSSE2310")."""
        return [course for course_list in self.course_dates_input.values() for course in course_list]

    @hybrid_property
    def course_dates(self) -> dict[tuple[int, int], list[str]]:
        return {
            tuple(map(int, k.replace("(", "").replace(")", "").split(","))): v
            for k, v in self.course_dates_input.items()
        }
