from serde import serde
from degree.validate_result import ValidateResult, Status

from degree.params import (
    ProgramRef,
    CourseRef,
    EquivalenceGroup,
    create_course_or_equivalence_from_dict
)
from api.plan import Plan
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
class SR:
    # Part, e.g. A or A.1
    part: str

    def validate(self, plan: Plan, course_getter, degree_getter) -> ValidateResult:
        return ValidateResult(Status.ERROR, None, "Should not be seeing this - validating abstract SR", plan.courses)


@serde
class SR1(SR):
    """Complete [N] units for ALL of the following"""

    n: int
    options: list[CourseRef | EquivalenceGroup]
    type: str = "SR1"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        
        async def _async_validate():
            count = 0
            badcourses = []
            
            for option in self.options:
                done = False
                for course in plan.courses:
                    if option.validate(course):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        done = True
                        break
                if not done:
                    badcourses.append(str(option))
            
            return count, badcourses
        
        # Run the async validation
        count, badcourses = _run_async(_async_validate())
        
        if count != self.n:
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100.0,
                f"{count} units found in plan, but {self.n} required. Add from: {', '.join(badcourses)}",
                badcourses,
            )
        elif badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100.0,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
        options = [str(option) for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} units for ALL of the following {options}", options)


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

    n: int
    m: int
    options: list[CourseRef | EquivalenceGroup]
    type: str = "SR2"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        
        async def _async_validate():
            count = 0
            badcourses = []
            donecourses = []
            
            for option in self.options:
                done = False
                for course in plan.courses:
                    if option.validate(course):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        donecourses.append(course)
                        done = True
                        break
                if not done:
                    badcourses.append(str(option))
            
            return count, badcourses, donecourses
        
        # Run the async validation
        count, badcourses, donecourses = _run_async(_async_validate())
        
        if count < self.n:
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100.0,
                f"{count} units found in plan, but {self.n} required. Add from: {', '.join(badcourses)}",
                badcourses,
            )
        elif count > self.m:
            return ValidateResult(Status.ERROR, count / self.m * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        if badcourses:
            return ValidateResult(Status.ERROR, (self.n - len(badcourses)) / self.n * 100.0,
                                  f"{', '.join(badcourses)} need to be in the plan", badcourses)
        options = [str(option) for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} to {self.m} units for ALL of the following {options}", options)


@serde
class SR3(SR):
    """Complete at least [N] units from the following"""

    n: int
    options: list[CourseRef | EquivalenceGroup]
    type: str = "SR3"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        
        async def _async_validate():
            count = 0
            badcourses = []
            
            for option in self.options:
                done = False
                for course in plan.courses:
                    if option.validate(course):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        done = True
                        break
                if not done:
                    badcourses.append(str(option))
            
            return count, badcourses
        
        # Run the async validation
        count, badcourses = _run_async(_async_validate())
        
        if count < self.n:
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(badcourses)}", badcourses)
        options = [str(option) for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete at least {self.n} units from the following {options}", options)



@serde
class SR4(SR):
    """Complete [N] to [M] units from the following"""

    n: int
    m: int
    options: list[CourseRef | EquivalenceGroup]
    type: str = "SR4"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        
        async def _async_validate():
            count = 0
            badcourses = []
            donecourses = []
            
            for option in self.options:
                done = False
                for course in plan.courses:
                    if option.validate(course):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        donecourses.append(course)
                        done = True
                        break
                if not done:
                    badcourses.append(str(option))
            
            return count, badcourses, donecourses
        
        # Run the async validation
        count, badcourses, donecourses = _run_async(_async_validate())
        
        if count < self.n:
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100.0,
                f"{count} units found in plan, but {self.n} required. Add from: {', '.join(badcourses)}",
                badcourses,
            )
        elif count > self.m:
            return ValidateResult(Status.ERROR, count / self.m * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        options = [str(option) for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete {self.n} to {self.m} units from the following {options}", options)


@serde
class SR5(SR):
    """Complete exactly [N] units from the following"""

    n: int
    options: list[CourseRef | EquivalenceGroup]
    type: str = "SR5"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        
        async def _async_validate():
            count = 0
            badcourses = []
            donecourses = []
            
            for option in self.options:
                done = False
                for course in plan.courses:
                    if option.validate(course):
                        course_model = await course_getter(course)
                        count += course_model.num_units if course_model else 0
                        donecourses.append(course)
                        done = True
                        break
                if not done:
                    badcourses.append(str(option))
            
            return count, badcourses, donecourses
        
        # Run the async validation
        count, badcourses, donecourses = _run_async(_async_validate())
        
        if count < self.n:
            return ValidateResult(
                Status.ERROR,
                count / self.n * 100.0,
                f"{count} units found in plan, but {self.n} required. Add from: {', '.join(badcourses)}",
                badcourses,
            )
        elif count > self.n:
            return ValidateResult(Status.ERROR, count / self.n * 100.0,
                                  f"{count} units found in plan, "
                                  f"but {self.n} required. Remove from: "
                                  f"{', '.join(donecourses)}", donecourses)
        options = [str(option) for option in self.options]
        return ValidateResult(Status.OK, 100.0, f"Complete exactly {self.n} units from the following", options)


@serde
class SR6(SR):
    """Complete one [PLANTYPE] from the following"""

    plan_type: str
    options: list[ProgramRef]
    type: str = "SR6"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        for option in self.options:
            for specialisation in plan.specialisations.get(self.part, []):
                if option.validate(specialisation):
                    # If the specialisation matches the option code
                    # we consider it valid
                    return ValidateResult(Status.OK, 100.0,
                                          f"Complete one {self.plan_type} from the following: {', '.join(str(opt) for opt in self.options)}",
                                          [str(opt) for opt in self.options])

        return ValidateResult(Status.ERROR, None,
                              f"No {self.plan_type} found in plan. "
                              f"Add from: {', '.join(str(opt) for opt in self.options)}",
                              [str(opt) for opt in self.options])

@serde
class SR7(SR):
    """Complete exactly [N] [PLANTYPES] from the following"""

    n: int
    plan_types: str
    options: list[ProgramRef]
    type: str = "SR7"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        count = 0
        doneoptions = []
        notdoneoptions = []
        for option in self.options:
            done = False
            for specialisation in plan.specialisations.get(self.part, []):
                if option.validate(specialisation):
                    count += 1
                    done = True
                    doneoptions.append(str(option))
                    break
            if not done:
                notdoneoptions.append(str(option))
        
        option_codes = [str(opt) for opt in self.options]
        
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(option_codes)}", notdoneoptions)
        elif count > self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Remove from: "
                                  f"{', '.join(option_codes)}", doneoptions)
        return ValidateResult(Status.OK, 100.0,
                              f"Complete exactly {self.n} {self.plan_types} "
                              f"from following {option_codes}", option_codes)


@serde
class SR8(SR):
    """Complete [N] to [M] [PLANTYPES] from the following"""

    n: int
    m: int
    plan_types: str  # Usually just major unless your course is weird
    options: list[ProgramRef]
    type: str = "SR8"

    def validate(self, plan: Plan,
                 course_getter: Callable[[str], Awaitable[CourseDBModel | None]],
                 degree_getter: Callable[[str, int], Awaitable[DegreeDBModel | None]]):
        count = 0
        doneoptions = []
        notdoneoptions = []
        for option in self.options:
            done = False
            for specialisation in plan.specialisations.get(self.part, []):
                if option.validate(specialisation):
                    count += 1
                    done = True
                    doneoptions.append(str(option))
                    break
            if not done:
                notdoneoptions.append(str(option))
        
        option_codes = [str(opt) for opt in self.options]
        
        if count < self.n:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.n} required. Add from: "
                                  f"{', '.join(option_codes)}", notdoneoptions)
        elif count > self.m:
            return ValidateResult(Status.ERROR, None,
                                  f"{count} {self.plan_types} found in plan, "
                                  f"but {self.m} maximum. Remove from: "
                                  f"{', '.join(option_codes)}", doneoptions)
        return ValidateResult(Status.OK, 100.0,
                              f"Complete {self.n} to {self.m} {self.plan_types} "
                              f"from following {option_codes}", option_codes)
    

def create_sr_from_dict(data: dict) -> SR:
    """Factory function to create correct SR subclass from dict."""
    sr_type = data.get("type", "SR")
    
    # Handle options field manually for SR rules that have Union types
    if sr_type in ["SR1", "SR2", "SR3", "SR4", "SR5"] and "options" in data:
        # Convert the options manually
        options_data = data["options"]
        converted_options = []
        for option_data in options_data:
            converted_options.append(
                create_course_or_equivalence_from_dict(option_data)
            )
        
        # Create a copy of data with converted options
        data_copy = data.copy()
        data_copy["options"] = converted_options
        
        type_map = {
            "SR1": SR1,
            "SR2": SR2,
            "SR3": SR3,
            "SR4": SR4,
            "SR5": SR5,
        }
        
        if sr_type in type_map:
            # Create the object manually since we can't use from_dict
            sr_class = type_map[sr_type]
            if sr_type in ["SR2", "SR4"]:
                return sr_class(
                    part=data_copy.get("part", ""),
                    n=data_copy["n"],
                    m=data_copy["m"],
                    options=data_copy["options"],
                    type=sr_type
                )
            else:
                return sr_class(
                    part=data_copy.get("part", ""),
                    n=data_copy["n"],
                    options=data_copy["options"],
                    type=sr_type
                )
    
    # For other types, use normal deserialization
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
