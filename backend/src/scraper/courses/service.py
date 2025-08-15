"""Courses scrape service."""

import asyncio
import logging
import random
from typing import NoReturn

import bs4
import curl_cffi
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import HttpUrl

from scraper.courses.models import Course, CourseLevel, CourseOffering, CourseSecatInfo

log = logging.getLogger(__name__)

# Requests things
MAX_CONCURRENT_REQUESTS = 10
RETRY_COUNT = 3
TIMEOUT_SECONDS = 60

# Urls
COURSES_URL = "https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses"
ECP_URL = "https://programs-courses.uq.edu.au/course.html?course_code={}"
SECAT_URL = "https://www.pbi.uq.edu.au/clientservices/SECaT/embedChart.aspx"


semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def get_secat_info() -> dict[str, CourseSecatInfo]:
    """Extracts course info from the secat, mapping a course code to the secat info."""
    results: dict[str, CourseSecatInfo] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SECAT_URL)
        await page.wait_for_selector(".rtsLevel1 .rtsLink .rtsTxt")

        letters = page.locator(".rtsLevel1 .rtsLink .rtsTxt")

        # this is getting A, B, C, etc.
        for i in range(await letters.count()):
            letter_elem = letters.nth(i)
            letter_text = await letter_elem.inner_text()
            log.info(f"[Level 1] Clicking letter: {letter_text}")

            await letter_elem.click()
            await asyncio.sleep(random.uniform(0.5, 2))  # noqa: S311

            # this is then getting ABTS, ACCT, ADVT, etc.
            await page.wait_for_selector(".rtsLevel2 .rtsLink .rtsTxt")
            courses_lvl2 = page.locator(".rtsLevel2 .rtsLink .rtsTxt")

            for j in range(await courses_lvl2.count()):
                course_lvl2_elem = courses_lvl2.nth(j)
                course_text = await course_lvl2_elem.inner_text()
                log.info(f"[Level 2] Clicking course: {course_text}")

                await course_lvl2_elem.click()
                await asyncio.sleep(random.uniform(0.5, 2))  # noqa: S311

                # this is then getting AGRC1010, AGRC1012, etc.
                await page.wait_for_selector(".rtsLevel3 .rtsLink .rtsTxt")

                courses_lvl3_texts = await page.locator(".rtsLevel3 .rtsLink .rtsTxt").all_inner_texts()

                log.info(f"Category {course_text} has {len(courses_lvl3_texts)} courses")

                for full_course_code in courses_lvl3_texts:
                    # re-locate the element each iteration to avoid stale reference
                    course_elem = page.locator(".rtsLevel3 .rtsLink .rtsTxt", has_text=full_course_code)

                    log.info(f"[Level 3] Clicking full course: {full_course_code}")
                    await course_lvl2_elem.click()  # expand parent
                    await course_elem.click()

                    await page.wait_for_selector("#lblNoEnrolled")
                    enrolled = int(await page.locator("#lblNoEnrolled").inner_text())
                    responses = int(await page.locator("#lblNoResponses").inner_text())
                    rate = float((await page.locator("#lblRespRate").inner_text()).replace("%", ""))

                    results[full_course_code] = CourseSecatInfo(
                        num_enrolled=enrolled, num_responses=responses, response_rate=rate
                    )

        await browser.close()

    return results


def _extract_course_html(html: str, course_code: str) -> Course | None:
    """Parses the ECP html into a course."""
    soup = BeautifulSoup(html, "html.parser")

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
    def _parse_offerings(table_id: str) -> list[CourseOffering]:
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

            profile_tag = row.select_one(".course-offering-profile a")
            if not profile_tag:
                _throw_parse_error("profile")

            profile_url: HttpUrl | None = profile_tag.get("href") if profile_tag else None
            offerings.append(CourseOffering(semester=sem, location=loc, mode=mode, profile_url=profile_url))
        return offerings

    current_offerings = _parse_offerings("course-current-offerings")
    archived_offerings = _parse_offerings("course-archived-offerings")

    return Course(
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
        faculty_url=None if not faculty_url else HttpUrl(faculty_url),
        school=school,
        duration=duration,
        attendance_mode=attendance_mode,
        class_hours=class_hours,
        course_enquries=course_enquiries,
        # Offerings
        current_offerings=current_offerings,
        archived_offerings=archived_offerings,
    )


async def _extract_course_info_ecp(session: curl_cffi.AsyncSession, course_code: str) -> Course | str:
    """Extracts the course info from the ecp."""
    log.debug(f"Fetching ecp info for course '{course_code}'")

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            r = await session.get(ECP_URL.format(course_code), timeout=TIMEOUT_SECONDS)
            r.raise_for_status()
            result = _extract_course_html(r.text, course_code)
            return result or course_code  # noqa: TRY300
        except curl_cffi.requests.exceptions.Timeout:
            log.warning(f"Timeout fetching course '{course_code}' (attempt {attempt}/{RETRY_COUNT})")
        except Exception:
            log.exception(f"Error fetching course '{course_code}' (attempt {attempt}/{RETRY_COUNT})")
        await asyncio.sleep(1)  # small delay before retry
    log.error(f"Failed to fetch course '{course_code}' after {RETRY_COUNT} attempts")
    return course_code


async def _extract_course_info_with_limit(session: curl_cffi.AsyncSession, course_code: str) -> Course | str:
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


async def scrape_courses() -> list[Course]:
    """Fetches all of the course info."""
    async with curl_cffi.AsyncSession() as session:
        try:
            r = await session.get(COURSES_URL)
            r.raise_for_status()
            course_codes = _parse_course_codes(r.text)

            # Get info from ecp
            courses: list[Course] = []
            skipped: list[str] = []

            tasks = [_extract_course_info_with_limit(session, code) for code in course_codes]
            course_results = await asyncio.gather(*tasks)

            for course in course_results:
                if isinstance(course, str):
                    log.error(f"Unable to get ECP for course '{course}'")
                    skipped.append(course)
                else:
                    courses.append(course)

        except Exception:
            log.exception("Error fetching courses")
            raise

        else:
            return courses
