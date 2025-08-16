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
        count = 0
        badcourses = []
        for option in self.options:
            if option.code not in plan.courses:
                badcourses.append(option.code)
            else:
                count += 2  # UPDATE UNITS
        if count != self.n:
            return ValidateResult(Status.ERROR, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

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
            return ValidateResult(Status.ERROR, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.m:
            return ValidateResult(Status.WARN, count / self.m * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        if badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
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
            return ValidateResult(Status.ERROR, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
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
            return ValidateResult(Status.ERROR, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.m:
            return ValidateResult(Status.WARN, count / self.m * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR5(SR):
    """Complete exactly [N] units from the following"""

    n: int
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
            return ValidateResult(Status.ERROR, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.n:
            return ValidateResult(Status.WARN, count / self.n * 100,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR6(SR):
    """Complete one [PLANTYPE] from the following"""

    plan_type: str
    options: list[ProgramRef]

    def validate(self, plan: Plan):
        option_codes = [opt.code for opt in self.options]
        if any(code in option_codes for code in plan.specialisations[self.part]):
            return ValidateResult(Status.OK, 100, "", [])
        else:
            return ValidateResult(Status.ERROR, None,
                                  f"No {self.plan_type} found in plan. "
                                  f"Add from: {', '.join(option_codes)}",
                                  option_codes)

@serde
class SR7(SR):
    """Complete exactly [N] [PLANTYPES] from the following"""

    n: int
    plan_types: str
    options: list[ProgramRef]

    def validate(self, plan: Plan):
        option_codes = [opt.code for opt in self.options]
        count = sum(1 for code in plan.specialisations[self.part]
                    if code in option_codes)
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(option_codes)}", option_codes)
        elif count > self.n:
            return ValidateResult(Status.WARN, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Remove from: "
                                  f"{', '.join(option_codes)}", option_codes)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class SR8(SR):
    """Complete [N] to [M] [PLANTYPES] from the following"""

    n: int
    m: int
    plan_types: str  # Usually just major unless your course is weird
    options: list[ProgramRef]

    def validate(self, plan: Plan):
        option_codes = [opt.code for opt in self.options]
        count = sum(1 for code in plan.specialisations[self.part]
                    if code in option_codes)
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(option_codes)}", option_codes)
        elif count > self.m:
            return ValidateResult(Status.WARN, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(option_codes)}", option_codes)
        return ValidateResult(Status.OK, 100, "", [])