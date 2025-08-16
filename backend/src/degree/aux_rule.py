"""Classes for auxiliary rules."""

from serde import serde
from serde.json import from_dict

from api.plan.plan import Plan
from degree.params import CourseRef, ProgramRef
from degree.validate_result import Status, ValidateResult


@serde
class AR:
    # Part, e.g. A or A.1
    part: str

    def validate(self, plan: Plan) -> ValidateResult:
        return ValidateResult(Status.ERROR, None, "Should not be seeing this - validating abstract AR", plan.courses)


@serde
class AR1(AR):
    """at least [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True
    type: str = "AR1"

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        exceptionCourse = ""
        try:
            for course in plan.courses:
                exceptionCourse = course
                course_level = int(course[4])
                if course_level == self.level or (course_level > self.level and self.or_higher):
                    count += 2  # change to units (ask lucas)
            if count >= self.n:
                return ValidateResult(Status.OK, 100, "", [])
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100,
                f"Expected at least {self.n} units at level {self.level}{' or higher' if self.or_higher else ''}, found {count}.",
                plan.courses,
            )
        except ValueError:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])


@serde
class AR2(AR):
    """at most [N] units at level [LEVEL]."""

    n: int
    level: int
    type: str = "AR2"

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        badcourses = []
        exceptionCourse = ""
        try:
            for course in plan.courses:
                exceptionCourse = course
                course_level = int(course[4])
                if course_level == self.level:
                    count += 2  # change to units (ask lucas)
                    badcourses.append(course)
            if count < self.n:
                return ValidateResult(Status.OK, 100, "", [])
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100,
                f"Expected at most {self.n} units at level {self.level}, found {count}.",
                badcourses,
            )
        except ValueError:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])


@serde
class AR3(AR):
    """exactly [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True
    type: str = "AR3"

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        badcourses = []
        exceptionCourse = ""
        try:
            for course in plan.courses:
                exceptionCourse = course
                course_level = int(course[4])
                if course_level == self.level or (course_level > self.level and self.or_higher):
                    count += 2  # change to units (ask lucas)
                    badcourses.append(course)
            if count == self.n:
                return ValidateResult(Status.OK, 100, "", [])
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100,
                f"Expected at most {self.n} units at level {self.level}, found {count}.",
                badcourses,
            )
        except ValueError:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])


@serde
class AR4(AR):
    """[N] to [M] units at level [LEVEL][OR_HIGHER]."""

    n: int
    m: int
    level: int
    or_higher: bool = True
    type: str = "AR4"

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        badcourses = []
        exceptionCourse = ""
        try:
            for course in plan.courses:
                exceptionCourse = course
                course_level = int(course[4])
                if course_level == self.level or (course_level > self.level and self.or_higher):
                    count += 2  # change to units (ask lucas)
                    badcourses.append(course)
            if count >= self.n and count <= self.m:
                return ValidateResult(Status.OK, 100, "", [])
            if count < self.n:
                return ValidateResult(
                    Status.ERROR,
                    count / self.n * 100,
                    f"Expected at least {self.n} units at level {self.level}, found {count}.",
                    badcourses,
                )
            return ValidateResult(
                Status.ERROR,
                count / self.m * 100,
                f"Expected at most {self.m} units at level {self.level}, found {count}.",
                badcourses,
            )
        except ValueError:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])


@serde
class AR5(AR):
    """[PLAN_LIST_1] only with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR5"

    def validate(self, plan: Plan) -> ValidateResult:
        for plan_ref in self.plan_list_1:
            if plan_ref.code in plan.specialisations[self.part]:
                values = [item for sublist in plan.specialisations.values() for item in sublist]
            if not set(self.plan_list_2) & set(values):
                return ValidateResult(
                    Status.ERROR,
                    None,
                    f"Expected {self.plan_list_1} to be with {self.plan_list_2}.",
                    plan.specialisations[self.part],
                )
            return ValidateResult(Status.OK, 100, "", [])
        return ValidateResult(Status.ERROR, None, "Unreachable", [])


@serde
class AR6(AR):
    """[PLAN_LIST_1] NOT with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR6"

    def validate(self, plan: Plan) -> ValidateResult:
        for plan_ref in self.plan_list_1:
            if plan_ref.code in plan.specialisations[self.part]:
                values = [item for sublist in plan.specialisations.values() for item in sublist]
                if set(self.plan_list_2) & set(values):
                    return ValidateResult(
                        Status.ERROR,
                        None,
                        f"Expected {self.plan_list_1} to NOT be with {self.plan_list_2}.",
                        plan.specialisations[self.part],
                    )
                return ValidateResult(Status.OK, 100, "", [])
        return ValidateResult(Status.ERROR, None, "Unreachable", [])


@serde
class AR7(AR):
    """No more than [N] units from same discipline descriptor."""

    n: int
    type: str = "AR7"

    def validate(self, plan: Plan) -> ValidateResult:
        discipline_count = {}
        discipline_lists = {}
        badlist = []
        totalcount = 0
        for course in plan.courses:
            discipline = course[:4]
            discipline_count[discipline] = discipline_count.get(discipline, 0) + 2  # REPLACE WITH UNITS
            discipline_lists[discipline].append(course)
        if any(count > self.n for count in discipline_count.values()):
            greater_than_n = [d for d, count in discipline_count.items() if count > self.n]
            for discipline in greater_than_n:
                badlist.extend(discipline_lists[discipline])
            return ValidateResult(Status.ERROR, totalcount / self.n * 100, "", badlist)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR9(AR):
    """No credit for [COURSE_LIST]."""

    course_list: list[CourseRef]
    type: str = "AR9"

    def validate(self, plan: Plan) -> ValidateResult:
        badcourses = []
        for course in plan.courses:
            if course in self.course_list:
                badcourses.append(course)
        if badcourses:
            return ValidateResult(Status.ERROR, None, f"No credit for {self.course_list}.", badcourses)
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR10(AR):
    """No credit for [COURSE_LIST] for students completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]
    type: str = "AR10"

    def validate(self, plan: Plan) -> ValidateResult:
        for plan_ref in self.plan_list:
            if plan_ref.code in plan.specialisations[self.part]:
                overlap = set(self.course_list) & set(plan.courses)
                if overlap:
                    return ValidateResult(
                        Status.ERROR,
                        0,
                        f"No credit for {overlap} for students completing {plan_ref}.",
                        list(overlap),
                    )
                return ValidateResult(Status.OK, 100, "", [])
        return ValidateResult(Status.ERROR, None, "Unreachable", [])


@serde
class AR11(AR):
    """No credit for [COURSE_LIST] unless completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]
    type: str = "AR11"

    def validate(self, plan: Plan) -> ValidateResult:
        overlap = set(self.course_list) & set(plan.courses)
        if overlap:
            if all(plan_ref.code not in plan.specialisations[self.part] for plan_ref in self.plan_list):
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"No credit for {overlap} for students not completing {self.plan_list}.",
                    list(overlap),
                )
            return ValidateResult(Status.OK, 100, "", [])
        return ValidateResult(Status.ERROR, None, "Unreachable", [])


@serde
class AR13(AR):
    """Students undertaking [PLAN_LIST] are exempt from [COURSE_LIST] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    program_plan_list: list[ProgramRef]
    type: str = "AR13"

    # This is such a crazy edge case i'm just not gonna bother - it reads
    """
    Students undertaking the BE(Hons) Specialisation in Chemical
    Engineering, BE(Hons) Specialisation in Civil Engineering, BE(Hons)
    Specialisation in Electrical Engineering, BE(Hons) Specialisation in
    Mechanical Engineering, or BE(Hons) Specialisation in Mechatronic
    Engineering are exempt from STAT2203 in the BA Major in Mathematics.
    """

    def validate(self, plan: Plan) -> ValidateResult:
        for plan_ref in self.plan_list:
            if plan_ref.code in plan.specialisations[self.part]:
                overlap = set(self.course_list) & set(plan.courses)
                if overlap:
                    return ValidateResult(
                        Status.ERROR,
                        0,
                        f"Students completing {plan_ref} are exempt from {overlap} in {self.program_plan_list}.",
                        list(overlap),
                    )
                return ValidateResult(Status.OK, 100, "", [])


@serde
class AR15(AR):
    """[COURSE_LIST] MUST/MAY be substituted in [PROGRAM_PLAN_LIST] by a course from [LISTS]."""

    course_list: list[CourseRef]
    must: bool  # True=MUST, False=MAY
    program_plan_list: list[ProgramRef]
    lists: list[str]  # reference names/ids to course lists
    type: str = "AR15"

    def validate(self, plan: Plan) -> ValidateResult:
        if self.must:
            # If it's a MUST, then we need to check that the course_list is in the program_plan_list
            overlap = set(self.course_list) & set(plan.courses)
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {self.course_list} to be substituted in {self.program_plan_list} by a course from {self.lists}.",
                    list(overlap),
                )
            return ValidateResult(Status.OK, 100, "", [])
        # If it's a MAY, we don't need to check anything
        overlap = set(self.course_list) & set(plan.courses)
        if overlap:
            return ValidateResult(
                Status.OK,
                100,
                f"{overlap} may be substituted in" + f"{self.program_plan_list} by a course from" + f"{self.lists}",
                overlap,
            )
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR16(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST_1] MUST/MAY be substituted by [COURSE_LIST_2] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list_1: list[CourseRef]
    must: bool
    course_list_2: list[CourseRef]
    program_plan_list: list[ProgramRef]
    type: str = "AR16"

    def validate(self, plan: Plan) -> ValidateResult:
        if self.must:
            overlap = set(self.course_list_1) & set(plan.courses)
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {self.course_list_1} to be substituted in {self.plan_list} by a course from {self.course_list_2} in {self.program_plan_list}.",
                    list(overlap),
                )
            return ValidateResult(Status.OK, 100, "", [])
        # If it's a MAY, we don't need to check anything
        overlap = set(self.course_list_1) & set(plan.courses)
        if overlap:
            return ValidateResult(
                Status.OK,
                100,
                f"{overlap} may be substituted in"
                f"{self.plan_list} by a course from"
                f"{self.course_list_2} in {self.program_plan_list}",
                overlap,
            )
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR17(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST] MUST/MAY be substituted by a course from [LISTS] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    must: bool
    program_plan_list: list[ProgramRef]
    lists: list[str]
    type: str = "AR17"

    def validate(self, plan: Plan) -> ValidateResult:
        if self.must:
            overlap = set(self.course_list) & set(plan.courses)
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {self.course_list} to be substituted in {self.plan_list} by a course from {self.lists} in {self.program_plan_list}.",
                    list(overlap),
                )
            return ValidateResult(Status.OK, 100, "", [])
        # If it's a MAY, we don't need to check anything
        overlap = set(self.course_list) & set(plan.courses)
        if overlap:
            return ValidateResult(
                Status.OK,
                100,
                f"{overlap} may be substituted in"
                f"{self.plan_list} by a course from"
                f"{self.lists} in {self.program_plan_list}",
                overlap,
            )
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR18(AR):
    """[COURSE_LIST] can only be counted towards the [PROGRAM] component of a dual."""

    course_list: list[CourseRef]
    program: ProgramRef
    type: str = "AR18"

    def validate(self, plan: Plan) -> ValidateResult:
        for course in plan.courses:
            if course in self.course_list:
                if self.program.code not in plan.specialisations[self.part]:
                    return ValidateResult(
                        Status.ERROR,
                        0,
                        f"{course} can only be counted towards the {self.program.name} component of a dual.",
                        [course],
                    )
        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR19(AR):
    """For students completing [PLAN_LIST], [COURSE_LIST] only counts towards [PROGRAM] component."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    program: ProgramRef
    type: str = "AR19"

    def validate(self, plan: Plan) -> ValidateResult:
        for plan_ref in self.plan_list:
            if plan_ref.code == plan.degree:
                for course in plan.courses:
                    if course in self.course_list:
                        if self.program.code not in plan.specialisations[self.part]:
                            return ValidateResult(
                                Status.ERROR,
                                0,
                                f"{course} only counts towards the {self.program.name} component for students completing {plan_ref}",
                                [course],
                            )

        return ValidateResult(Status.OK, 100, "", [])


@serde
class AR20(AR):
    """For students completing [PLAN] and [PLAN_LIST_1], [COURSE_LIST] only counts towards [PLAN_LIST_2]."""

    plan_1: ProgramRef
    plan_list_1: list[ProgramRef]
    course_list: list[CourseRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR20"

    def validate(self, plan: Plan) -> ValidateResult:
        if plan.degree == self.plan_1.code:
            for plan_ref in self.plan_list_1:
                if plan_ref.code in plan.specialisations[self.part]:
                    for course in plan.courses:
                        if course in self.course_list:
                            if plan.specialisations[self.part] not in self.plan_list_2:
                                return ValidateResult(
                                    Status.ERROR,
                                    0,
                                    f"{course} only counts towards {self.plan_list_2} for students completing {plan_ref}.",
                                    [course],
                                )

        return ValidateResult(Status.OK, 100, "", [])


@serde
class ARUnknown(AR):
    """Fallback to preserve anything unexpected (future-proof)."""

    text: str
    raw_params: list[dict]


def create_ar_from_dict(data: dict) -> AR:
    """Factory function to create correct AR subclass from dict."""
    ar_type = data.get("type", "AR")

    type_map = {
        "AR1": AR1,
        "AR2": AR2,
        "AR3": AR3,
        "AR4": AR4,
        "AR5": AR5,
        "AR6": AR6,
        "AR7": AR7,
        "AR9": AR9,
        "AR10": AR10,
        "AR11": AR11,
        "AR13": AR13,
        "AR15": AR15,
        "AR16": AR16,
        "AR17": AR17,
        "AR18": AR18,
        "AR19": AR19,
        "AR20": AR20,
        "ARUnknown": ARUnknown,
    }

    if ar_type in type_map:
        return from_dict(type_map[ar_type], data)
    return from_dict(AR, data)
