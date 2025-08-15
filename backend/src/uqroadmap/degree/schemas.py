"""Degree schemas."""

from uqroadmap.schemas import UQRoadmapBase


class DegreeRead(UQRoadmapBase):
    """Degree schema read."""

    degree_id: int
    title: str


class DegreeCreate(UQRoadmapBase):
    """Degree schema create."""

    degree_id: int
    title: str
