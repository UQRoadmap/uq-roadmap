"""Script utils."""

from pathlib import Path

import orjson

from common.schemas import SecatInfo
from scraper.courses.models import ScrapedCourse
from scripts.constants import COURSES_FILE_NAME, SECATS_FILE_NAME


def load_courses() -> list[ScrapedCourse]:
    """Get all the unique modes."""
    with Path.open(Path(COURSES_FILE_NAME), "rb") as f:
        data = orjson.loads(f.read())

    return [ScrapedCourse(**course) for course in data["courses"]]


def load_secats() -> dict[str, SecatInfo]:
    """Get all the unique modes."""
    result = {}
    with Path.open(Path(SECATS_FILE_NAME), "r", encoding="utf-8") as file:
        for line in file:
            cleaned = line.strip()
            if cleaned:
                obj = orjson.loads(cleaned)
                course_code = obj["course"]
                secat = SecatInfo(**obj)
                result[course_code] = secat

    return result
