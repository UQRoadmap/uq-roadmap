"""Plan schemas."""

from typing import Literal
from uuid import UUID

from pydantic import computed_field, field_validator

from api.degree.schemas import DegreeRead
from common.schemas import UQRoadmapBase
from degree.validate_result import ValidateResult


class PlanBase(UQRoadmapBase):
    # maps (year, sem) -> course_codes e.g., 'CSSE2310"
    course_dates_input: dict[str, list[str]]

    @field_validator("course_dates_input", mode="before")
    @classmethod
    def validate_course_dates_keys(cls, v):
        """Ensure keys are comma-separated year,sem integers."""
        if not isinstance(v, dict):
            raise TypeError("course_dates_input must be a dict")

        for k in v.keys():
            parts = k.replace("(", "").replace(")", "").split(",")
            print(parts)
            if len(parts) != 2:
                raise ValueError(f"Key '{k}' must contain exactly two comma-separated values")
            try:
                year, sem = map(int, parts)
            except ValueError as e:
                raise ValueError(f"Key '{k}' must contain integers, got '{k}' - {e}")
        return v

    @computed_field  # type: ignore[misc]
    @property
    def course_dates(self) -> dict[tuple[int, int], list[str]]:
        """Go from json type to mcarthur type."""
        return {
            tuple(map(int, k.replace("(", "").replace(")", "").split(","))): v
            for k, v in self.course_dates_input.items()
        }


class PlanRead(PlanBase):
    """Plan read schema."""

    plan_id: UUID
    degree: DegreeRead

    name: str
    start_year: int
    start_sem: Literal[1, 2]
    end_year: int | None = None

    # maps (part) -> course_code list
    course_reqs: dict[str, list[str]]

    # maps (part) -> degree code (e.g., "2525")
    specialisations: dict[str, list[str]]

    courses: list[str]

    validation_results: list[ValidateResult] | None = None


class PlanCreateUpdate(PlanBase):
    """Plan create/update schema."""

    degree_id: UUID
    name: str

    start_year: int
    start_sem: Literal[1, 2]
    end_year: int

    # maps (part) -> course_code list
    course_reqs: dict[str, list[str]]

    # maps (part) -> degree code (e.g., "2525")
    specialisations: dict[str, list[str]]
