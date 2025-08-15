"""Scraper models."""

import logging

import httpx
from bs4 import BeautifulSoup, Tag
import cloudscraper

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
            logger.warning("Skipping row with insufficient columns: {}", row)
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


def scrape_all_courses() -> list[Course]:
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(COURSES_URL, headers=HEADERS)
        response.raise_for_status()
        return parse_courses(response.text)
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []