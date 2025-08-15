"""A Complete User Plan."""

from uuid import UUID


class Plan:
    name: str
    plan_id: UUID
    auth: UUID
    # maps (year, sem) to list of chosen courses
    courses: dict[tuple[int, int], list[str]]
