from enum import Enum

from pydantic import BaseModel, computed_field


class UQScrapeModel(BaseModel):
    """Base model for UQ scrape models."""


class Program(UQScrapeModel):
    title: str
    url: str
    program_id: str


class CourseLevel(Enum):
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    OTHER = "other"


class CourseOffering(UQScrapeModel):
    semester: str
    location: str
    mode: str


class Course(UQScrapeModel):
    code: str
    name: str
    level: CourseLevel
    num_units: float
    offerings: list[CourseOffering]

    @computed_field
    @property
    def active(self) -> bool:
        return bool(self.offerings)
