"""Classes for auxiliary rules."""

from serde import serde, AdjacentTagging

from degree.params import CourseRef, ProgramRef
from degree.validate_result import ValidateResult, Status
from api.plan import Plan


@serde(tagging=AdjacentTagging("code", "data"))
class AR:
    def validate(plan) -> ValidateResult:
        return ValidateResult(Status.ERROR, None, "Should not be seeing this", [])


@serde
class AR1(AR):
    """at least [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        try:
            for course in plan.courses:
                course_level = int(course[4])
                if course_level == self.level or \
                        (course_level > self.level and self.or_higher):
                    count += -1  # change to units (ask lucas)
            if count >= self.n:
                return ValidateResult(Status.OK, 100, "", [])
            else:
                return ValidateResult(
                    Status.ERROR,
                    count / self.n * 100,
                    f"Expected at least {self.n} units at level {self.level}{' or higher' if self.or_higher else ''}, found {count}.",
                    plan.courses,
                )
        except ValueError:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", plan.courses)


@serde
class AR2(AR):
    """at most [N] units at level [LEVEL]."""

    n: int
    level: int

    def validate(self, plan: Plan) -> ValidateResult:
        count = 0
        badcourses = []
        try:
            for course in plan.courses:
                course_level = int(course[4])
                if course_level == self.level:
                    count += -1  # change to units (ask lucas)
                    badcourses.append(course)
            if count < self.n:
                return ValidateResult(Status.OK, 100, "", [])
            else:
                return ValidateResult(Status.ERROR, count / self.n * 100,
                                    f"Expected at most {self.n} units at level {self.level}, found {count}.", badcourses)
        except ValueError:
            return ValidateResult(Status.ERROR, None,
                                  "Invalid course level format", plan.courses)


@serde
class AR3(AR):
    """exactly [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True


@serde
class AR4(AR):
    """[N] to [M] units at level [LEVEL][OR_HIGHER]."""

    n: int
    m: int
    level: int
    or_higher: bool = True


@serde
class AR5(AR):
    """[PLAN_LIST_1] only with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]


@serde
class AR6(AR):
    """[PLAN_LIST_1] NOT with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]


@serde
class AR7(AR):
    """No more than [N] units from same discipline descriptor."""

    n: int


@serde
class AR9(AR):
    """No credit for [COURSE_LIST]."""

    course_list: list[CourseRef]


@serde
class AR10(AR):
    """No credit for [COURSE_LIST] for students completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]


@serde
class AR11(AR):
    """No credit for [COURSE_LIST] unless completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]


@serde
class AR13(AR):
    """Students undertaking [PLAN_LIST] are exempt from [COURSE_LIST] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    program_plan_list: list[ProgramRef]


@serde
class AR15(AR):
    """[COURSE_LIST] MUST/MAY be substituted in [PROGRAM_PLAN_LIST] by a course from [LISTS]."""

    course_list: list[CourseRef]
    must: bool  # True=MUST, False=MAY
    program_plan_list: list[ProgramRef]
    lists: list[str]  # reference names/ids to course lists


@serde
class AR16(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST_1] MUST/MAY be substituted by [COURSE_LIST_2] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list_1: list[CourseRef]
    must: bool
    course_list_2: list[CourseRef]
    program_plan_list: list[ProgramRef]


@serde
class AR17(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST] MUST/MAY be substituted by a course from [LISTS] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    must: bool
    program_plan_list: list[ProgramRef]
    lists: list[str]


@serde
class AR18(AR):
    """[COURSE_LIST] can only be counted towards the [PROGRAM] component of a dual."""

    course_list: list[CourseRef]
    program: ProgramRef


@serde
class AR19(AR):
    """For students completing [PLAN_LIST], [COURSE_LIST] only counts towards [PROGRAM] component."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    program: ProgramRef


@serde
class AR20(AR):
    """For students completing [PLAN] and [PLAN_LIST_1], [COURSE_LIST] only counts towards [PLAN_LIST_2]."""

    plan: ProgramRef
    plan_list_1: list[ProgramRef]
    course_list: list[CourseRef]
    plan_list_2: list[ProgramRef]


@serde
class ARUnknown(AR):
    """Fallback to preserve anything unexpected (future-proof)."""

    text: str
    raw_params: list[dict]
