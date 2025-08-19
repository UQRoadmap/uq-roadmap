from serde import serde
from degree.validate_result import ValidateResult, Status


@serde
class Param:
    def validate(self, item: str) -> ValidateResult:
        """Validates that item matches the param.
        Item might be a course code or program code."""
        return ValidateResult(Status.OK, None, "", [])


@serde
class CourseRef(Param):
    # Params meeting the type=Course
    units_max: int | None
    units_min: int | None
    code: str
    org_name: str
    org_code: str
    name: str

    def validate(self, item: str) -> bool:
        """Validates that item matches the course code."""
        print(f"Validating {item} against {self.code}")
        if item == self.code:
            return True
        else:
            return False
    
    def __str__(self) -> str:
        return f"{self.code}"


@serde
class EquivalenceGroup(Param):
    courses: list[CourseRef]
    notes: str | None

    def validate(self, item: str) -> bool:
        """Validates that item matches one of the course codes in the group."""
        for course in self.courses:
            if course.validate(item):
                return True
        return False
    
    def __str__(self) -> str:
        return f"({' or '.join(str(course) for course in self.courses)})"


@serde
class WildCardItem(Param):
    notes: str | None
    code: str
    org_name: str | None
    org_code: str | None
    include_child_orgs: bool
    type: str


def create_course_or_equivalence_from_dict(data: dict) -> (
    CourseRef | EquivalenceGroup
):
    """Factory function to create CourseRef or EquivalenceGroup from dict."""
    # Handle new format where objects are wrapped with type name as key
    if 'CourseRef' in data:
        return _create_course_ref_safely(data['CourseRef'])
    elif 'EquivalenceGroup' in data:
        return _create_equivalence_group_safely(data['EquivalenceGroup'])
    
    # Check if there's an explicit type field (legacy format)
    if 'type' in data:
        if data['type'] in ['course', 'CourseRef']:
            return _create_course_ref_safely(data)
        elif data['type'] in ['equivalence', 'EquivalenceGroup']:
            return _create_equivalence_group_safely(data)
    
    # Fallback: If it has 'courses' field, it's an EquivalenceGroup
    if 'courses' in data:
        return _create_equivalence_group_safely(data)
    # Otherwise, it's a CourseRef (has fields like 'code', 'units_max', etc.)
    else:
        return _create_course_ref_safely(data)


def _create_course_ref_safely(data: dict) -> CourseRef:
    """Safely create a CourseRef with proper defaults for missing fields."""
    return CourseRef(
        units_max=data.get('units_max') or data.get('unitsMaximum'),
        units_min=data.get('units_min') or data.get('unitsMinimum'),
        code=data.get('code', ''),
        org_name=data.get('org_name', '') or data.get('orgName', ''),
        org_code=data.get('org_code', '') or data.get('orgCode', ''),
        name=data.get('name', ''),
    )


def _create_equivalence_group_safely(data: dict) -> EquivalenceGroup:
    """Safely create an EquivalenceGroup with proper defaults."""
    courses = []
    courses_data = data.get('courses', [])
    
    for course_data in courses_data:
        if isinstance(course_data, dict):
            courses.append(_create_course_ref_safely(course_data))
        else:
            # If it's just a string code, create a minimal CourseRef
            courses.append(CourseRef(
                units_max=None,
                units_min=None,
                code=str(course_data),
                org_name='',
                org_code='',
                name='',
            ))
    
    return EquivalenceGroup(
        courses=courses,
        notes=data.get('notes'),
    )


@serde
class ProgramRef(Param):
    # Params meeting the type=Program Rqt
    units_max: int | None
    units_min: int | None
    code: str
    org_name: str
    org_code: str
    name: str
    abbreviation: str

    def validate(self, item: str) -> bool:
        """Validates that item matches the program code."""
        print(f"Validating {item} against {self.code}")
        if item == self.code:
            return True
        else:
            return False
        
    def __str__(self) -> str:
        return f"{self.code}"