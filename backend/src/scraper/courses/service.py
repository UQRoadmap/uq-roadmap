"""Courses scrape service."""

import asyncio
import logging
from pathlib import Path
from typing import NoReturn

import bs4
import curl_cffi
from bs4 import BeautifulSoup

from common.enums import CourseLevel
from scraper.courses.models import AssessmentItem, ScrapedCourse, ScrapedCourseOffering

log = logging.getLogger(__name__)

# Requests things
MAX_CONCURRENT_REQUESTS = 30
RETRY_COUNT = 3
TIMEOUT_SECONDS = 60

# Urls
COURSES_URL = "https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses"
ECP_URL = "https://programs-courses.uq.edu.au/course.html?course_code={}"

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def _get_webpage(session: curl_cffi.AsyncSession, url: str) -> str:
    cache_file = CACHE_DIR / f"{url.replace('/', '_').replace(':', '')}.html"

    if cache_file.exists():
        log.info(f"Cached page for {url} exists")
        return cache_file.read_text(encoding="utf-8")

    # get it online
    r = await session.get(url, timeout=TIMEOUT_SECONDS)
    r.raise_for_status()
    html = r.text
    cache_file.write_text(html, encoding="utf-8")

    return html


def _extract_assessment_html(html: str) -> list[AssessmentItem] | None:
    soup = BeautifulSoup(html, "html.parser")
    assessments: list[AssessmentItem] = []
    # Extract assessment information from the soup

    sections = soup.select("#assessment-details h3")
    if sections is None or len(sections) == 0:
        return None

    for section in sections:
        task = section.get_text(strip=True)

        # Navigate siblings (dl contains structured data)
        dl = section.find_next("dl")
        details = {
            dt.get_text(strip=True): dd.get_text(" ", strip=True)
            for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd"), strict=False)
        }

        category = details.get("Category")
        mode = details.get("Mode")
        weight = details.get("Weight")
        due_date = details.get("Due date")
        learning_outcomes = (
            details.get("Learning outcomes", "").replace(" ", "").split(",") if "Learning outcomes" in details else []
        )

        # Flags (hurdle, identity verified)
        flags = [li.get_text(strip=True) for li in section.find_next("ul").find_all("li")]
        hurdle = any("Hurdle" in f for f in flags)
        identity_verified = any("Identity Verified" in f for f in flags)

        task_div = section.find_next("h4", string="Task description")
        task_description = None
        if task_div:
            task_p = task_div.find_next("div", class_="collapsible")
            if task_p:
                task_description = task_p.get_text(" ", strip=True)

        weight = weight.strip().replace("%", "") if weight else None
        weight_val = (float(weight) / 100 if weight.isnumeric() else None) if weight is not None else None

        assessments.append(
            AssessmentItem(
                task=task,
                category=category,
                description=task_description,
                weight=weight_val,
                due_date=due_date,
                mode=mode,
                learning_outcomes=learning_outcomes,
                hurdle=hurdle,
                identity_verified=identity_verified,
            )
        )

    return assessments


async def _extract_assessment_info(session: curl_cffi.AsyncSession, profile_url: str) -> list[AssessmentItem] | None:
    html = await _get_webpage(session, profile_url)

    return _extract_assessment_html(html)


async def _extract_course_html(session: curl_cffi.AsyncSession, html: str, course_code: str) -> ScrapedCourse | None:  # noqa: C901, PLR0912, PLR0915
    """Parses the ECP html into a course."""
    soup = BeautifulSoup(html, "html.parser")

    not_found_tag = soup.select_one("#course-notfound")

    if not_found_tag:
        log.warning(f"Course '{course_code}' not found.")
        return None

    description_div = soup.find("div", id="description")
    if description_div and "not currently offered" in description_div.get_text():
        return None

    def _throw_parse_error(attribute: str) -> NoReturn:
        raise AttributeError(f"Can't determine '{attribute}' for course '{course_code}'")

    # Core info
    title_text_tag = soup.select_one("#course-title")
    if not title_text_tag:
        _throw_parse_error("title")

    title_text = title_text_tag.text.strip()
    if "(" in title_text and ")" in title_text:
        name, code = title_text.rsplit("(", 1)
        name = name.strip()
        code = code.rstrip(")").strip()
    else:
        name = title_text
        code = ""

    description_tag = soup.select_one("#course-summary")
    if not description_tag:
        _throw_parse_error("description")

    description = description_tag.text.strip()

    level_tag = soup.select_one("#course-level")
    if not level_tag:
        _throw_parse_error("level")

    level_str = level_tag.text.strip().lower()
    level = CourseLevel(level_str) if level_str in CourseLevel._value2member_map_ else CourseLevel.OTHER
    if level is CourseLevel.OTHER:
        log.warning(f"Level for course '{course_code}' was passed as OTHER")

    num_units_tag = soup.select_one("#course-units")
    if not num_units_tag:
        _throw_parse_error("num_units")

    num_units = float(num_units_tag.text.strip())  # Why is ACCT1101E worth 3.2 units

    incompatible_tag = soup.select_one("#course-incompatible")
    incompatible = incompatible_tag.text.strip() if incompatible_tag else None

    prerequisite_tag = soup.select_one("#course-prerequisite")
    prerequisite = prerequisite_tag.text.strip() if prerequisite_tag else None

    # Misc Info
    faculty_tag = soup.select_one("#course-faculty")

    if not faculty_tag:
        _throw_parse_error("faculty_tag")

    faculty = faculty_tag.text.strip()
    faculty_url = faculty_tag.get("href") if faculty_tag else None

    school_tag = soup.select_one("#course-school")
    if not school_tag:
        _throw_parse_error("school")
    school = school_tag.text.strip()

    duration = 1  # Derived from "One Semester"
    attendance_mode_tag = soup.select_one("#course-mode")
    if not attendance_mode_tag:
        _throw_parse_error("attendance_mode")

    attendance_mode: str = attendance_mode_tag.text.strip()

    class_hours_tag = soup.select_one("#course-contact")

    class_hours = (
        class_hours_tag.decode_contents().replace("<br/>", "\n").replace("<br />", "\n").strip()
        if class_hours_tag
        else None
    )
    course_enquiries_tag = soup.select_one("#course-coordinator p")
    course_enquiries = course_enquiries_tag.text.strip() if course_enquiries_tag else None

    # Offerings
    def _parse_offerings(table_id: str) -> list[ScrapedCourseOffering]:
        offerings = []
        for row in soup.select(f"#{table_id} tbody tr"):
            sem_tag = row.select_one("a.course-offering-year")
            if not sem_tag:
                _throw_parse_error("sem")
            sem = sem_tag.text.strip()

            loc_tag = row.select_one(".course-offering-location")
            if not loc_tag:
                _throw_parse_error("location")
            loc = loc_tag.text.strip()

            mode_tag = row.select_one(".course-offering-mode")
            if not mode_tag:
                _throw_parse_error("mode")
            mode = mode_tag.text.strip()

            profile_link_tag = row.select_one(".course-offering-profile a")

            profile_url = None
            if profile_link_tag:
                profile_url = str(profile_link_tag.get("href"))
            else:
                log.warning(f"{course_code} profile unavailable for {sem_tag.text.strip()} ({table_id})")

            offerings.append(ScrapedCourseOffering(semester=sem, location=loc, mode=mode, profile_url=profile_url))
        return offerings

    current_offerings = _parse_offerings("course-current-offerings")
    archived_offerings = _parse_offerings("course-archived-offerings")

    asessment_info: list[AssessmentItem] | None = None
    for offering in current_offerings:
        if not offering.profile_url:
            continue
        asessment_info = await _extract_assessment_info(session, offering.profile_url)
        if asessment_info:
            log.info(f"Found assessment info for {course_code} in offering {offering.semester}")
            break

    if asessment_info is not None:
        log.info(f"Looking in archived courses for assessment info for course {course_code}...")
        for offering in archived_offerings:
            if not offering.profile_url:
                continue
            asessment_info = await _extract_assessment_info(session, offering.profile_url)
            if asessment_info:
                log.info(f"Found assessment info for {course_code} in archived offering {offering.semester}")
                break

    return ScrapedCourse(
        # General info
        code=course_code,
        name=name,
        description=description,
        level=level,
        num_units=num_units,
        incompatible=incompatible,
        prerequisite=prerequisite,
        # Misc info
        faculty=faculty,
        faculty_url=str(faculty_url) if faculty_url else None,
        school=school,
        duration=duration,
        attendance_mode=attendance_mode,
        class_hours=class_hours,
        course_enquries=course_enquiries,
        # Offerings
        current_offerings=current_offerings,
        archived_offerings=archived_offerings,
        latest_assessment=asessment_info,
        secat=None,
    )


async def _extract_course_info_ecp(session: curl_cffi.AsyncSession, course_code: str) -> ScrapedCourse | str:
    """Extracts the course info from the ecp."""
    log.debug(f"Fetching ecp info for course '{course_code}'")

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            html = await _get_webpage(session, ECP_URL.format(course_code))
            result = await _extract_course_html(session, html, course_code)

            return result or course_code  # noqa: TRY300
        except curl_cffi.requests.exceptions.Timeout:
            log.warning(f"Timeout fetching course '{course_code}' (attempt {attempt}/{RETRY_COUNT})")
        except Exception:
            log.exception(f"Error fetching course '{course_code}' (attempt {attempt}/{RETRY_COUNT})")
        await asyncio.sleep(1)  # small delay before retry
    log.error(f"Failed to fetch course '{course_code}' after {RETRY_COUNT} attempts")
    return course_code


async def _extract_course_info_with_limit(session: curl_cffi.AsyncSession, course_code: str) -> ScrapedCourse | str:
    """Wrap extraction with semaphore to limit concurrency."""
    async with semaphore:
        return await _extract_course_info_ecp(session, course_code)


def _parse_course_codes(html: str) -> list[str]:
    """Parses the list of courses page and grabs the name from each.

    https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses

    Args:
        html (str): html from https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses

    Returns:
        list[str]: list of course codes
    """
    soup = BeautifulSoup(html, "html.parser")
    container: bs4.PageElement | None = soup.find("div", id="courses-container")
    if not container:
        log.warning("No courses found")
        return []

    list_items = container.select("ul.listing > li")

    return [li.find("a", class_="code").get_text(strip=True) for li in list_items]


async def scrape_courses() -> list[ScrapedCourse]:
    """Fetches all of the course info."""
    async with curl_cffi.AsyncSession() as session:
        try:
            html = await _get_webpage(session, COURSES_URL)

            course_codes = _parse_course_codes(html)

            # Get info from ecp
            courses: list[ScrapedCourse] = []
            skipped: list[str] = []

            tasks = [_extract_course_info_with_limit(session, code) for code in course_codes]
            course_results = await asyncio.gather(*tasks)

            for course in course_results:
                if isinstance(course, str):
                    log.error(f"Unable to get ECP for course '{course}'")
                    skipped.append(course)
                else:
                    courses.append(course)

            if skipped:
                log.error(f"Couldn't get data for the following courses: '[{', '.join(skipped)}]'")

        except Exception:
            log.exception("Error fetching courses")
            raise

        else:
            return courses
