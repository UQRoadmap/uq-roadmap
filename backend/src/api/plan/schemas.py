"""Plan schemas."""

from typing import Literal
from uuid import UUID

from api.degree.schemas import DegreeRead
from common.schemas import UQRoadmapBase


class PlanRead(UQRoadmapBase):
    """Plan read schema."""

    plan_id: UUID
    degree: DegreeRead

    name: str
    start_year: int
    start_sem: Literal[1, 2]
    end_year: int | None = None

    # maps (year, sem) -> course_codes e.g., 'CSSE2310"
    course_dates: dict[tuple[int, int], list[str]]

    # maps (part) -> course_code list
    course_reqs: dict[str, list[str]]

    # maps (part) -> degree code (e.g., "2525")
    specialisations: dict[str, list[str]]

    courses: list[str]


class PlanCreateUpdate(UQRoadmapBase):
    """Plan create/update schema."""

    degree_id: UUID
    name: str

    start_year: int
    start_sem: Literal[1, 2]
    end_year: int

    # maps (year, sem) -> course_codes e.g., 'CSSE2310"
    course_dates: dict[tuple[int, int], list[str]]

    # maps (part) -> course_code list
    course_reqs: dict[str, list[str]]

    # maps (part) -> degree code (e.g., "2525")
    specialisations: dict[str, list[str]]
