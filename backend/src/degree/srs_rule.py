from serde import serde
from degree.validate_result import ValidateResult, Status

from degree.params import ProgramRef, CourseRef
from api.plan import Plan


@serde
class SR:
    # Part, e.g. A or A.1
    part: str

    def validate(self, plan: Plan) -> ValidateResult:
        return ValidateResult(Status.OK, None, "", [])


@serde
class SR1(SR):
    """Complete [N] units for ALL of the following"""

    n: int
    options: list[CourseRef]

    def validate(self, plan: Plan):
        for option in self.options:
            if option.code not in plan.courses:
                return ValidateResult(Status.ERROR, None,
                                      f"Course {option.code}" +
                                      "not found in plan", option)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

    n: int
    m: int
    options: list[CourseRef]

    def validate(self, plan: Plan):
        for option in self.options:
            if option.code not in plan.courses:
                return ValidateResult(Status.ERROR, None,
                                      f"Course {option.code}" +
                                      "not found in plan", option)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR3(SR):
    """Complete at least [N] units from the following"""

    n: int
    options: list[CourseRef]

    def validate(self, plan: Plan):
        count = 0
        badcourses = []
        for course in self.options:
            if course.code in plan.courses:
                count += 2  # UPDATE UNITS
            else:
                badcourses.append(course.code)
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Missing: "
                                  f"{', '.join(badcourses)}", badcourses)
        return ValidateResult(Status.OK, 100, "", [])



@serde
class SR4(SR):
    """Complete [N] to [M] units from the following"""

    n: int
    m: int
    options: list[CourseRef]

    def validate(self, plan: Plan):
        count = 0
        badcourses = []
        donecourses = []
        for course in self.options:
            if course.code in plan.courses:
                count += 2  # UPDATE UNITS
                donecourses.append(course.code)
            else:
                badcourses.append(course.code)
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Missing: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.m:
            return ValidateResult(Status.WARN, None,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Done: "
                                  f"{', '.join(donecourses)}", donecourses)
        return ValidateResult(Status.OK, 100, "", [])


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
