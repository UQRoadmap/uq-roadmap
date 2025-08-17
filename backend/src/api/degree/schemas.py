"""Degree schemas."""

from uuid import UUID

from common.schemas import UQRoadmapBase


class DegreeRead(UQRoadmapBase):
    """Degree schema read."""

    degree_id: UUID
    degree_code: str
    year: int

    title: str
    degree_url: str | None = None


class DegreeSummary(UQRoadmapBase):
    """Degrees summary."""

    title: str
    degree_code: str
    years: list[int]
