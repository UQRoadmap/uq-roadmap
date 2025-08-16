"""Seeding DB with initial data."""

import json
import logging
from collections.abc import Generator
from pathlib import Path

import orjson
from sqlalchemy.ext.asyncio import AsyncSession

from api.courses.models import CourseDBModel
from api.courses.transformers import transform_scraped_course
from api.degree.models import DegreeDBModel
from scraper.courses.models import ScrapedCourse

from serde.json import from_dict, to_dict, to_json

from scraper.degree import Degree as ParsedDegree

from degree.converter import convert_degree

DATA_DIR = Path("data")
COURSES_FILE = DATA_DIR / "complete_courses.json"
DEGREES_FILE = DATA_DIR / "program_details.json"


log = logging.getLogger(__name__)


async def seed_db(session: AsyncSession, populate_courses: bool, populate_degrees: bool) -> None:  # noqa: D103, FBT001
    log.info("Checking if database needs to be seeded")
    if populate_courses:
        log.info("Seeding courses from file: %s", COURSES_FILE)
        for course in load_courses_from_file():
            session.add(course)

    if populate_degrees:
        log.info("Seeding degrees from file: %s", DEGREES_FILE)
        for degree in load_degrees_from_file():
            session.add(degree)

    await session.commit()


def load_courses_from_file() -> Generator[CourseDBModel]:
    """Loads courses from a JSON file and hydrates CourseDBModel instances."""
    with Path.open(COURSES_FILE, "rb") as f:
        data = orjson.loads(f.read())

    scraped_courses = [ScrapedCourse(**course) for course in data["courses"]]

    for course in scraped_courses:
        yield transform_scraped_course(course)


def load_degrees_from_file() -> Generator[DegreeDBModel]:
    """Loads degrees from a JSON file and hydrates DegreeDBModel instances."""
    with Path.open(DEGREES_FILE, "rb") as f:
        raw = f.read()
        details = json.loads(raw)["program_details"]

        for detail in details:
            for year, data in detail["data"].items():
                degree: ParsedDegree = from_dict(ParsedDegree | None, data)
                if degree is None:
                    continue

                flat = convert_degree(degree)

                degree_db_model = DegreeDBModel(degree_id=str(flat.code), title=flat.name, json=to_json(flat))

                yield degree_db_model
