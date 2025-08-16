"""Seeding DB with initial data."""

import json
import logging
from pathlib import Path

import orjson
from serde.json import from_dict, to_json
from sqlalchemy.ext.asyncio import AsyncSession

from api.courses.models import CourseDBModel
from api.courses.transformers import transform_scraped_course
from api.degree.models import DegreeDBModel
from degree.converter import convert_degree
from scraper.courses.models import ScrapedCourse
from scraper.degree import Degree as ParsedDegree

DATA_DIR = Path("data")
COURSES_FILE = DATA_DIR / "complete_courses.json"
DEGREES_FILE = DATA_DIR / "program_details.json"
DEGREES_META_FILE = DATA_DIR / "program_meta.json"

log = logging.getLogger(__name__)


async def seed_db(session: AsyncSession, populate_courses: bool, populate_degrees: bool) -> None:  # noqa: D103, FBT001
    log.info("Checking if database needs to be seeded")
    if not populate_courses:
        log.info("Seeding courses from file: %s", COURSES_FILE)
        for course in load_courses_from_file():
            session.add(course)

    if populate_degrees:
        log.info("Seeding degrees from file: %s", DEGREES_FILE)
        for degree in load_degrees_from_file():
            session.add(degree)

    await session.commit()


def load_courses_from_file() -> list[CourseDBModel]:
    """Loads courses from a JSON file and hydrates CourseDBModel instances."""
    with Path.open(COURSES_FILE, "rb") as f:
        data = orjson.loads(f.read())

    scraped_courses = [ScrapedCourse(**course) for course in data["courses"]]

    return [transform_scraped_course(c) for c in scraped_courses]


def load_degrees_from_file() -> list[DegreeDBModel]:
    """Loads degrees from a JSON file and hydrates DegreeDBModel instances."""
    degree_meta_map: dict[str, tuple[str, str]] = {}  # mapping degree_id to (name, degree_url)
    result = []
    with Path.open(DEGREES_META_FILE, "rb") as f:
        data = orjson.loads(f.read())
        for meta in data:
            degree_meta_map[meta["program_id"]] = (meta["title"], meta["url"])

    with Path.open(DEGREES_FILE, "rb") as f:
        raw = f.read()
        details = json.loads(raw)["program_details"]

        for detail in details:
            for data in detail["data"].values():
                degree: ParsedDegree = from_dict(ParsedDegree | None, data)
                if degree is None:
                    continue

                flat = convert_degree(degree)

                if flat.code not in degree_meta_map:
                    # thanks UQ :)
                    continue

                degree_title, degree_url = degree_meta_map[flat.code]
                year = int(flat.year)

                degree_db_model = DegreeDBModel(
                    degree_code=flat.code, year=year, title=degree_title, details=to_json(flat), degree_url=degree_url
                )

                result.append(degree_db_model)

    return result
