"""A Complete User Plan."""

from uuid import UUID


class Plan:
    name: str
    plan_id: UUID
    auth: UUID
    # maps (year, sem) to list of chosen courses
    course_dates: dict[tuple[int, int], list[str]]
    course_reqs: dict[str, list[str]]
    courses: list[str]
    degree: str
    specialisations: dict[str, list[str]]
