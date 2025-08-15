"""Scraper models."""

import logging

import httpx
from bs4 import BeautifulSoup, Tag

from scraper.models import Course, CourseLevel, CourseOffering

COURSES_URL = "https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses"
ECP_URL = "https://programs-courses.uq.edu.au/course.html?course_code={}"

HEADERS = {"User-Agent": "Mozilla/5.0"}

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
            log.warning("Skipping row with insufficient columns: %s", row)
            continue

        semester = cols[0].get_text(strip=True)
        location = cols[1].get_text(strip=True)
        mode = cols[2].get_text(strip=True)

        offerings.append(CourseOffering(semester=semester, location=location, mode=mode))

    return offerings


async def parse_course(li: Tag, client: httpx.AsyncClient) -> Course:
    """Parses a couse into a Course model."""
    code: str = li.find("a", class_="code").get_text(strip=True)
    name: str = li.find("a", class_="title").get_text(strip=True)
    level_text: str = li.find("span", class_="course-level").get_text(strip=True).lower()
    num_units_text: str = li.find("span", class_="course-units").get_text(strip=True).lower()

    block_div = li.find("div", class_="toggle-container").find("div", class_="block")
    offerings = parse_offerings(block_div)

    level = CourseLevel(level_text) if level_text in CourseLevel.__members__ else CourseLevel.OTHER

    ecp_response = await client.get(ECP_URL.format(code))
    ecp_response.raise_for_status()

    return Course(
        code=code,
        name=name,
        level=level,
        num_units=float(num_units_text),
        offerings=offerings,
    )


async def parse_courses(html: str, client: httpx.AsyncClient) -> list[Course]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", id="courses-container")
    if not container:
        log.warning("No courses found")
        return []

    return [await parse_course(li, client) for li in container.select("ul.listing > li")]


async def scrape_all_courses() -> list[Course]:
    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        response = await client.get(COURSES_URL)
        response.raise_for_status()
    return await parse_courses(response.text, client)
