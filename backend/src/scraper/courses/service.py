"""Courses scrape service."""

import logging

import curl_cffi
from bs4 import BeautifulSoup, Tag

from scraper.courses.constants import COURSES_URL
from scraper.models import Course, CourseLevel, CourseOffering

log = logging.getLogger(__name__)


def parse_offerings(block_div: Tag) -> list[CourseOffering]:
    offerings: list[CourseOffering] = []
    table = block_div.find("table")
    if not table:
        return offerings

    rows = table.find_all("tr")

    data_rows = rows[2:-1]

    for row in data_rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            log.warning(f"Skipping row with insufficient columns: {row}")
            continue

        semester = cols[0].get_text(strip=True)
        location = cols[1].get_text(strip=True)
        mode = cols[2].get_text(strip=True)

        offerings.append(CourseOffering(semester=semester, location=location, mode=mode))

    return offerings


def parse_course(li: Tag) -> Course:
    code: str = li.find("a", class_="code").get_text(strip=True)
    name: str = li.find("a", class_="title").get_text(strip=True)
    level_text: str = li.find("span", class_="course-level").get_text(strip=True).lower()
    num_units_text: str = li.find("span", class_="course-units").get_text(strip=True).lower()

    block_div = li.find("div", class_="toggle-container").find("div", class_="block")
    offerings = parse_offerings(block_div)

    level = CourseLevel(level_text) if level_text in CourseLevel.__members__ else CourseLevel.OTHER

    return Course(
        code=code,
        name=name,
        level=level,
        num_units=float(num_units_text),
        offerings=offerings,
    )


def parse_courses(html: str) -> list[Course]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", id="courses-container")
    if not container:
        log.warning("No courses found")
        return []

    return [parse_course(li) for li in container.select("ul.listing > li")]


async def scrape_courses() -> list[Course]:
    """Fetches all of the course info."""
    async with curl_cffi.AsyncSession() as session:
        try:
            r = await session.get(COURSES_URL)
            r.raise_for_status()
            return parse_courses(r.text)
        except Exception:
            log.exception("Error fetching courses")
            raise
