from serde import serde, AdjacentTagging
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
    version_minor: int
    version_major: int


@serde
class EquivalenceGroup(Param):
    courses: list[CourseRef]
    notes: str | None


@serde
class WildCardItem(Param):
    notes: str | None
    code: str
    org_name: str | None
    org_code: str | None
    include_child_orgs: bool
    type: str


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
    version_minor: int
    version_major: int
