"""Classes for auxiliary rules."""

from serde import AdjacentTagging, serde

from api.plan import Plan
from degree.params import CourseRef, ProgramRef
from degree.validate_result import Status, ValidateResult
from typing import Callable, Awaitable
from api.courses.models import CourseDBModel
from api.degree.models import DegreeDBModel
import asyncio

from serde.json import from_dict


def _run_async(coro):
    """Helper function to run async code from sync context."""
    try:
        # Try to get the current event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # Event loop is running, need to use different approach
        # This will create a new thread with its own event loop
        import concurrent.futures
        
        def run_in_thread():
            return asyncio.run(coro)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

@serde
class AR:
    # Part, e.g. A or A.1
    part: str

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        return ValidateResult(
            Status.ERROR, None, "Should not be seeing this - validating abstract AR", plan.courses, self.part
        )


@serde
class AR1(AR):
    """at least [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True
    type: str = "AR1"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        
        async def _async_validate():
            count = 0
            validcourses = []
            exceptionCourse = ""
            try:
                for course in plan.courses:
                    exceptionCourse = course
                    course_level = int(course[4])
                    if course_level == self.level or (course_level > self.level and self.or_higher):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        validcourses.append(course)
                return count, validcourses, exceptionCourse, None
            except ValueError as e:
                return None, None, exceptionCourse, str(e)
        
        # Run the async validation
        result = _run_async(_async_validate())
        count, validcourses, exceptionCourse, error = result
        
        if error:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])
        
        if count >= self.n:
            return ValidateResult(Status.OK, 100.0, "", [])
        return ValidateResult(
            Status.ERROR,
            count / self.n * 100.0,
            f"Expected at least {self.n} units at level {self.level}{' or higher' if self.or_higher else ''}, found {count}.",
            validcourses,
        )


@serde
class AR2(AR):
    """at most [N] units at level [LEVEL]."""

    n: int
    level: int
    type: str = "AR2"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        
        async def _async_validate():
            count = 0
            badcourses = []
            exceptionCourse = ""
            try:
                for course in plan.courses:
                    exceptionCourse = course
                    course_level = int(course[4])
                    if course_level == self.level:
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        badcourses.append(course)
                return count, badcourses, exceptionCourse, None
            except ValueError as e:
                return None, None, exceptionCourse, str(e)
        
        # Run the async validation
        result = _run_async(_async_validate())
        count, badcourses, exceptionCourse, error = result
        
        if error:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])
        
        if count <= self.n:
            return ValidateResult(Status.OK, 100.0, "", [])
        return ValidateResult(
            Status.ERROR,
            count / self.n * 100.0,
            f"Expected at most {self.n} units at level {self.level}, found {count}.",
            badcourses,
        )


@serde
class AR3(AR):
    """exactly [N] units at level [LEVEL][OR_HIGHER]."""

    n: int
    level: int
    or_higher: bool = True
    type: str = "AR3"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        
        async def _async_validate():
            count = 0
            levelcourses = []
            exceptionCourse = ""
            try:
                for course in plan.courses:
                    exceptionCourse = course
                    course_level = int(course[4])
                    if course_level == self.level or (course_level > self.level and self.or_higher):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        levelcourses.append(course)
                return count, levelcourses, exceptionCourse, None
            except ValueError as e:
                return None, None, exceptionCourse, str(e)
        
        # Run the async validation
        result = _run_async(_async_validate())
        count, levelcourses, exceptionCourse, error = result
        
        if error:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])
        
        if count == self.n:
            return ValidateResult(Status.OK, 100.0, "", [])
        return ValidateResult(
            Status.ERROR,
            count / self.n * 100.0,
            f"Expected exactly {self.n} units at level {self.level}, found {count}.",
            levelcourses,
        )


@serde
class AR4(AR):
    """[N] to [M] units at level [LEVEL][OR_HIGHER]."""

    n: int
    m: int
    level: int
    or_higher: bool = True
    type: str = "AR4"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        
        async def _async_validate():
            count = 0
            levelcourses = []
            exceptionCourse = ""
            try:
                for course in plan.courses:
                    exceptionCourse = course
                    course_level = int(course[4])
                    if course_level == self.level or (course_level > self.level and self.or_higher):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        levelcourses.append(course)
                return count, levelcourses, exceptionCourse, None
            except ValueError as e:
                return None, None, exceptionCourse, str(e)
        
        # Run the async validation
        result = _run_async(_async_validate())
        count, levelcourses, exceptionCourse, error = result
        
        if error:
            return ValidateResult(Status.ERROR, None, "Invalid course level format", [exceptionCourse])
        
        if count >= self.n and count <= self.m:
            return ValidateResult(Status.OK, 100.0, "", [])
        if count < self.n:
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100.0,
                f"Expected at least {self.n} units at level {self.level}, found {count}.",
                levelcourses,
            )
        return ValidateResult(
            Status.ERROR,
            count / self.m * 100.0,
            f"Expected at most {self.m} units at level {self.level}, found {count}.",
            levelcourses,
        )


@serde
class AR5(AR):
    """[PLAN_LIST_1] only with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR5"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        matching_plans = []
        required_plans = []
        
        for plan_ref in self.plan_list_1:
            for specialisation in plan.specialisations.get(self.part, []):
                if plan_ref.validate(specialisation):
                    matching_plans.append(plan_ref.code)
                    break
        
        if matching_plans:
            # Check if any of plan_list_2 is present
            values = [item for sublist in plan.specialisations.values() for item in sublist]
            for plan_ref in self.plan_list_2:
                if plan_ref.validate(values):
                    required_plans.append(plan_ref.code)
            
            if not required_plans:
                return ValidateResult(
                    Status.ERROR,
                    None,
                    f"Expected {[str(p) for p in self.plan_list_1]} to be with {[str(p) for p in self.plan_list_2]}.",
                    [str(p) for p in self.plan_list_2],
                    self.part,
                )
            return ValidateResult(Status.OK, 100.0, "", [], self.part)
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR6(AR):
    """[PLAN_LIST_1] NOT with [PLAN_LIST_2]."""

    plan_list_1: list[ProgramRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR6"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        matching_plans = []
        conflicting_plans = []
        
        for plan_ref in self.plan_list_1:
            for specialisation in plan.specialisations.get(self.part, []):
                if plan_ref.validate(specialisation):
                    matching_plans.append(plan_ref.code)
                    break
        
        if matching_plans:
            # Check if any of plan_list_2 is present (conflict)
            values = [item for sublist in plan.specialisations.values()
                      for item in sublist]
            for plan_ref in self.plan_list_2:
                for value in values:
                    if plan_ref.validate(value):
                        conflicting_plans.append(plan_ref.code)
                        break
            
            if conflicting_plans:
                return ValidateResult(
                    Status.ERROR,
                    None,
                    f"Expected {[str(p) for p in self.plan_list_1]} to NOT be "
                    f"with {[str(p) for p in self.plan_list_2]}.",
                    conflicting_plans,
                )
            return ValidateResult(Status.OK, 100.0, "", [])
        return ValidateResult(Status.OK, 100.0, "", [])


@serde
class AR7(AR):
    """No more than [N] units from same discipline descriptor."""

    n: int
    type: str = "AR7"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        
        async def _async_validate():
            discipline_count = {}
            discipline_lists = {}
            for course in plan.courses:
                discipline = course[:4]
                course_model = await course_getter(course)
                units = course_model.num_units if course_model else 0
                discipline_count[discipline] = discipline_count.get(discipline, 0) + units
                if discipline not in discipline_lists:
                    discipline_lists[discipline] = []
                discipline_lists[discipline].append(course)
            return discipline_count, discipline_lists
        
        # Run the async validation
        discipline_count, discipline_lists = _run_async(_async_validate())
        
        badlist = []
        totalcount = 0
        if any(count > self.n for count in discipline_count.values()):
            greater_than_n = [d for d, count in discipline_count.items() if count > self.n]
            for discipline in greater_than_n:
                badlist.extend(discipline_lists[discipline])
            return ValidateResult(Status.ERROR, totalcount / self.n * 100.0, "", badlist, self.part)
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR9(AR):
    """No credit for [COURSE_LIST]."""

    course_list: list[CourseRef]
    type: str = "AR9"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        badcourses = []
        for course_ref in self.course_list:
            for course in plan.courses:
                if course_ref.validate(course):
                    badcourses.append(course)
        
        if badcourses:
            return ValidateResult(Status.ERROR, None,
                                  f"No credit for {[str(c) for c in self.course_list]}.",
                                  badcourses, self.part)
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR10(AR):
    """No credit for [COURSE_LIST] for students completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]
    type: str = "AR10"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        for plan_ref in self.plan_list:
            for specialisation in plan.specialisations.get(self.part, []):
                if plan_ref.validate(specialisation):
                    overlap = []
                    for course_ref in self.course_list:
                        for course in plan.courses:
                            if course_ref.validate(course):
                                overlap.append(course)
                    
                    if overlap:
                        return ValidateResult(
                            Status.ERROR,
                            0,
                            f"No credit for {overlap} for students "
                            f"completing {plan_ref}.",
                            overlap,
                            self.part,
                    )
                    return ValidateResult(Status.OK, 100.0, "", [], self.part)
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR11(AR):
    """No credit for [COURSE_LIST] unless completing [PLAN_LIST]."""

    course_list: list[CourseRef]
    plan_list: list[ProgramRef]
    type: str = "AR11"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        overlap = []
        for course_ref in self.course_list:
            for course in plan.courses:
                if course_ref.validate(course):
                    overlap.append(course)
        
        if overlap:
            # Check if any plan from plan_list is present
            has_required_plan = False
            for plan_ref in self.plan_list:
                for specialisation in plan.specialisations.get(self.part, []):
                    if plan_ref.validate(specialisation):
                        has_required_plan = True
                        break
                if has_required_plan:
                    break
            
            if not has_required_plan:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"No credit for {overlap} for students not "
                    f"completing {[str(p) for p in self.plan_list]}.",
                    overlap,
                    self.part,
                )
            return ValidateResult(Status.OK, 100.0, "", [], self.part)
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


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

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        for plan_ref in self.plan_list:
            for specialisation in plan.specialisations.get(self.part, []):
                if plan_ref.validate(specialisation):
                    overlap = []
                    for course_ref in self.course_list:
                        for course in plan.courses:
                            if course_ref.validate(course):
                                overlap.append(course)
                    
                    if overlap:
                        return ValidateResult(
                            Status.ERROR,
                            0,
                            f"Students completing {plan_ref} are exempt from "
                            f"{overlap} in {[str(p) for p in self.program_plan_list]}.",
                            overlap,
                            self.part,
                    )
                    return ValidateResult(Status.OK, 100.0, "", [])
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR15(AR):
    """[COURSE_LIST] MUST/MAY be substituted in [PROGRAM_PLAN_LIST] by a course from [LISTS]."""

    course_list: list[CourseRef]
    must: bool  # True=MUST, False=MAY
    program_plan_list: list[ProgramRef]
    lists: list[str]  # reference names/ids to course lists
    type: str = "AR15"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        overlap = []
        for course_ref in self.course_list:
            for course in plan.courses:
                if course_ref.validate(course):
                    overlap.append(course)
        
        if self.must:
            # If it's a MUST, then we need to check that the course_list is present
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {[str(c) for c in self.course_list]} to be "
                    f"substituted in {[str(p) for p in self.program_plan_list]} "
                    f"by a course from {self.lists}.",
                    [str(c) for c in self.course_list],
                    self.part,
                )
            return ValidateResult(Status.OK, 100.0, "", [], self.part)
        # If it's a MAY, we don't need to check anything
        if overlap:
            return ValidateResult(
                Status.OK,
                100.0,
                f"{overlap} may be substituted in "
                f"{[str(p) for p in self.program_plan_list]} by a course from "
                f"{self.lists}",
                overlap,
                self.part,
            )
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR16(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST_1] MUST/MAY be substituted by [COURSE_LIST_2] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list_1: list[CourseRef]
    must: bool
    course_list_2: list[CourseRef]
    program_plan_list: list[ProgramRef]
    type: str = "AR16"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        overlap = []
        for course_ref in self.course_list_1:
            for course in plan.courses:
                if course_ref.validate(course):
                    overlap.append(course)
        
        if self.must:
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {[str(c) for c in self.course_list_1]} to be "
                    f"substituted in {[str(p) for p in self.plan_list]} by a "
                    f"course from {[str(c) for c in self.course_list_2]} in "
                    f"{[str(p) for p in self.program_plan_list]}.",
                    [str(c) for c in self.course_list_1],
                    self.part,
                )
            return ValidateResult(Status.OK, 100.0, "", [], self.part)
        # If it's a MAY, we don't need to check anything
        if overlap:
            return ValidateResult(
                Status.OK,
                100.0,
                f"{overlap} may be substituted in "
                f"{[str(p) for p in self.plan_list]} by a course from "
                f"{[str(c) for c in self.course_list_2]} in "
                f"{[str(p) for p in self.program_plan_list]}",
                overlap,
                self.part,
            )
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR17(AR):
    """For students in [PLAN_LIST] - [COURSE_LIST] MUST/MAY be substituted by a course from [LISTS] in [PROGRAM_PLAN_LIST]."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    must: bool
    program_plan_list: list[ProgramRef]
    lists: list[str]
    type: str = "AR17"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        overlap = []
        for course_ref in self.course_list:
            for course in plan.courses:
                if course_ref.validate(course):
                    overlap.append(course)
        
        if self.must:
            if not overlap:
                return ValidateResult(
                    Status.ERROR,
                    0,
                    f"Expected {[str(c) for c in self.course_list]} to be "
                    f"substituted in {[str(p) for p in self.plan_list]} by a "
                    f"course from {self.lists} in "
                    f"{[str(p) for p in self.program_plan_list]}.",
                    [str(c) for c in self.course_list],
                    self.part,
                )
            return ValidateResult(Status.OK, 100.0, "", [], self.part)
        # If it's a MAY, we don't need to check anything
        if overlap:
            return ValidateResult(
                Status.OK,
                100.0,
                f"{overlap} may be substituted in "
                f"{[str(p) for p in self.plan_list]} by a course from "
                f"{self.lists} in {[str(p) for p in self.program_plan_list]}",
                overlap,
                self.part,
            )
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR18(AR):
    """[COURSE_LIST] can only be counted towards the [PROGRAM] component of a dual."""

    course_list: list[CourseRef]
    program: ProgramRef
    type: str = "AR18"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        for course_ref in self.course_list:
            for course in plan.courses:
                if course_ref.validate(course):
                    for specialisation in plan.specialisations.get(self.part, []):
                        if not self.program.validate(specialisation):
                            return ValidateResult(
                                Status.ERROR,
                                0,
                                f"{course} can only be counted towards the "
                                f"{self.program.name} component of a dual.",
                                [course],
                                self.part,
                    )
        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR19(AR):
    """For students completing [PLAN_LIST], [COURSE_LIST] only counts towards [PROGRAM] component."""

    plan_list: list[ProgramRef]
    course_list: list[CourseRef]
    program: ProgramRef
    type: str = "AR19"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        for plan_ref in self.plan_list:
            if plan_ref.validate(plan.degree):
                for course_ref in self.course_list:
                    for course in plan.courses:
                        if course_ref.validate(course):
                            has_required_program = False
                            for specialisation in plan.specialisations.get(self.part, []):
                                if self.program.validate(specialisation):
                                    has_required_program = True
                                    break
                            
                            if not has_required_program:
                                return ValidateResult(
                                    Status.ERROR,
                                    0,
                                    f"{course} only counts towards the "
                                    f"{self.program.name} component for students "
                                    f"completing {plan_ref}",
                                    [course],
                                    self.part,
                            )

        return ValidateResult(Status.OK, 100.0, "", [], self.part)


@serde
class AR20(AR):
    """For students completing [PLAN] and [PLAN_LIST_1], [COURSE_LIST] only counts towards [PLAN_LIST_2]."""

    plan_1: ProgramRef
    plan_list_1: list[ProgramRef]
    course_list: list[CourseRef]
    plan_list_2: list[ProgramRef]
    type: str = "AR20"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]) -> ValidateResult:
        if self.plan_1.validate(plan.degree):
            for plan_ref in self.plan_list_1:
                for specialisation in plan.specialisations.get(self.part, []):
                    if plan_ref.validate(specialisation):
                        for course_ref in self.course_list:
                            for course in plan.courses:
                                if course_ref.validate(course):
                                    # Check if course only counts towards plan_list_2
                                    valid_for_plan_list_2 = False
                                    for target_plan in self.plan_list_2:
                                        for spec in plan.specialisations.get(self.part, []):
                                            if target_plan.validate(spec):
                                                valid_for_plan_list_2 = True
                                                break
                                        if valid_for_plan_list_2:
                                            break
                                    
                                    if not valid_for_plan_list_2:
                                        return ValidateResult(
                                            Status.ERROR,
                                            0,
                                            f"{course} only counts towards "
                                            f"{[str(p) for p in self.plan_list_2]} "
                                            f"for students completing {plan_ref}.",
                                            [course],
                                            self.part,
                                )

        return ValidateResult(Status.OK, 100.0, "", [], self.part)


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
    else:
        return from_dict(AR, data)
