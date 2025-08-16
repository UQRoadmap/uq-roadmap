"""Degree requirements representation."""

from collections.abc import Awaitable, Callable

from serde import serde

from api.course.models import CourseDBModel
from api.degree.models import DegreeDBModel
from api.plan.plan import Plan
from degree.aux_rule import AR
from degree.sr_rule import SR
from degree.validate_result import ValidateResult

CourseCallback = Callable[[str], Awaitable[CourseDBModel | None]]
DegreeCallback = Callable[[str, int], Awaitable[DegreeDBModel | None]]


@serde
class Degree:
    name: str
    code: str
    year: str
    sem: int

    # ALL aux rules associated with this course.
    # Aux rules (and SRS) conveniently have a ref, e.g. "A" or "A.1"
    # They can use that when passed the course info
    aux: list[AR]
    srs: list[SR]

    # Categories relevant to this degree.
    # Maps category a/b/c/d etc to its name
    # e.g. "A" -> "MPcompSci 1.5 Year DUration"
    # and  "A.1" -> "MCompSci Flexible Core Courses"
    part_references: dict[str, str]

    # Rule logic that operates broadly on the categories.
    # An entry might be A and B or A.1 OR B.1
    rule_logic: list[str]

    def validate(
        self, plan: Plan, course_getter: CourseCallback, degree_getter: DegreeCallback
    ) -> list[ValidateResult]:
        # Things to do:
        # -
        results = []
        for aux in self.aux:
            results.append(aux.validate(plan))
        for srs in self.srs:
            results.append(srs.validate(plan))

        return results

    @staticmethod
    def build() -> "Degree":
        return Degree(
            name="",
            code="",
            year="",
            sem=1,
            aux=list(),
            srs=list(),
            part_references=dict(),
            rule_logic=list(),
        )
