from serde import serde
from degree.validate_result import ValidateResult, Status

from degree.params import ProgramRef, CourseRef


@serde
class SR:
    # Part, e.g. A or A.1
    part: str

    def validate(plan) -> ValidateResult:
        return ValidateResult(Status.OK, None, "", [])


@serde
class SR1(SR):
    """Complete [N] units for ALL of the following"""

    n: int
    options: list[CourseRef]


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

    n: int
    m: int
    options: list[CourseRef]


@serde
class SR3(SR):
    """Complete at least [N] units from the following"""

    n: int
    options: list[CourseRef]


@serde
class SR4(SR):
    """Complete [N] to [M] units from the following"""

    n: int
    m: int
    options: list[CourseRef]


@serde
class SR5(SR):
    """Complete exactly [N] units from the following"""

    n: int
    options: list[CourseRef]


@serde
class SR6(SR):
    """Complete one [PLANTYPE] from the following"""

    plan_type: str
    options: list[ProgramRef]


@serde
class SR7(SR):
    """Complete exactly [N] [PLANTYPES] from the following"""

    n: int
    plan_types: str
    options: list[ProgramRef]


@serde
class SR8(SR):
    """Complete [N] to [M] [PLANTYPES] from the following"""

    n: int
    m: int
    plan_types: str  # Usually just major unless your course is weird
    options: list[ProgramRef]
