from serde import serde
from degree.validate_result import ValidateResult, Status

from degree.params import ProgramRef, CourseRef
from api.plan import Plan

from serde.json import from_dict

@serde
class SR:
    # Part, e.g. A or A.1
    part: str

    def validate(self, plan: Plan) -> ValidateResult:
        return ValidateResult(Status.ERROR, None, "Should not be seeing this - validating abstract SR", plan.courses)


@serde
class SR1(SR):
    """Complete [N] units for ALL of the following"""

    n: int
    options: list[CourseRef]
    type: str = "SR1"

    def validate(self, plan: Plan, course_getter, degree_getter):
        count = 0
        badcourses = []
        for option in self.options:
            if option.code not in plan.courses:
                badcourses.append(option.code)
            else:
                count += 2  # UPDATE UNITS
        if count != self.n:
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100.0,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} units for ALL of the following {options}", options)


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

    n: int
    m: int
    options: list[CourseRef]
    type: str = "SR2"

    def validate(self, plan: Plan, course_getter, degree_getter):
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
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.m:
            return ValidateResult(Status.WARN, count / self.m * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        if badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100.0,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} to {self.m} units for ALL of the following {options}", options)


@serde
class SR3(SR):
    """Complete at least [N] units from the following"""

    n: int
    options: list[CourseRef]
    type: str = "SR3"

    def validate(self, plan: Plan, course_getter, degree_getter):
        count = 0
        badcourses = []
        for course in self.options:
            if course.code in plan.courses:
                count += 2  # UPDATE UNITS
            else:
                badcourses.append(course.code)
        if count < self.n:
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete at least {self.n} units from the following {options}", options)



@serde
class SR4(SR):
    """Complete [N] to [M] units from the following"""

    n: int
    m: int
    options: list[CourseRef]
    type: str = "SR4"

    def validate(self, plan: Plan, course_getter, degree_getter):
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
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.m:
            return ValidateResult(Status.WARN, count / self.m * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} to {self.m} units from the following {options}", options)


@serde
class SR5(SR):
    """Complete exactly [N] units from the following"""

    n: int
    options: list[CourseRef]
    type: str = "SR5"

    def validate(self, plan: Plan, course_getter, degree_getter):
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
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        elif count > self.n:
            return ValidateResult(Status.WARN, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete exactly {self.n} units from the following", options)


@serde
class SR6(SR):
    """Complete one [PLANTYPE] from the following"""

    plan_type: str
    options: list[ProgramRef]
    type: str = "SR6"

    def validate(self, plan: Plan, course_getter, degree_getter):
        option_codes = [opt.code for opt in self.options]
        if any(code in option_codes for code in plan.specialisations.get(self.part, {})):
            options = [option.code for option in options]
            return ValidateResult(Status.OK, 100.0, f"Complete one {self.plan_type} from the following", options)
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
    type: str = "SR7"

    def validate(self, plan: Plan, course_getter, degree_getter):
        option_codes = [opt.code for opt in self.options]
        count = sum(1 for code in plan.specialisations.get(self.part, {})
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
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete exactly {self.n} {self.plan_types} from the following {options}", options)


@serde
class SR8(SR):
    """Complete [N] to [M] [PLANTYPES] from the following"""

    n: int
    m: int
    plan_types: str  # Usually just major unless your course is weird
    options: list[ProgramRef]
    type: str = "SR8"

    def validate(self, plan: Plan, course_getter, degree_getter):
        option_codes = [opt.code for opt in self.options]
        count = sum(1 for code in plan.specialisations.get(self.part, {})
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
        options = [option.code for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} to {self.m} {self.plan_types} from the following {options}", options)
    

def create_sr_from_dict(data: dict) -> SR:
    """Factory function to create correct SR subclass from dict."""
    sr_type = data.get("type", "SR")
    
    type_map = {
        "SR1": SR1,
        "SR2": SR2,
        "SR3": SR3,
        "SR4": SR4,
        "SR5": SR5,
        "SR6": SR6,
        "SR7": SR7,
        "SR8": SR8,
    }
    
    if sr_type in type_map:
        return from_dict(type_map[sr_type], data)
    else:
        return from_dict(SR, data)
    