"""Courses module."""

from .secats import iter_secat_info
from .service import scrape_courses

__all__ = ["iter_secat_info", "scrape_courses"]
