"""Base models."""

from common.schemas import UQRoadmapBase


class Program(UQRoadmapBase):
    """Program schema."""

    title: str
    url: str
    program_id: str
