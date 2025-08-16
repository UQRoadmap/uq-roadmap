from serde import serde, AdjacentTagging


@serde
class CourseRef:
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
class ProgramRef:
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
