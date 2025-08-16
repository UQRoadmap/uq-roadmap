"""Course schemas."""

from common.schemas import UQRoadmapBase


class CourseRead(UQRoadmapBase):
    """Read schema for course."""


class CourseReadDetailed(CourseRead):
    """Detailed read schema for course."""
