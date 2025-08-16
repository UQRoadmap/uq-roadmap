"""Base models."""

from pydantic import BaseModel


class UQScrapeModel(BaseModel):
    """Base model for UQ scrape models."""


class Program(UQScrapeModel):
    title: str
    url: str
    program_id: str
