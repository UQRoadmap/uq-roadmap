"""Courses scrape service."""

import asyncio
import json
import logging
import re
from collections import defaultdict
from collections.abc import AsyncGenerator
from typing import NoReturn

import bs4
import curl_cffi
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from common.enums import CourseLevel
from scraper.courses.models import Course, CourseOffering, CourseSecatInfo, SecatQuestion

log = logging.getLogger(__name__)

# Requests things
MAX_CONCURRENT_REQUESTS = 30
RETRY_COUNT = 3
TIMEOUT_SECONDS = 60

# Urls
COURSES_URL = "https://programs-courses.uq.edu.au/search.html?keywords=*&searchType=all&archived=true#courses"
ECP_URL = "https://programs-courses.uq.edu.au/course.html?course_code={}"
SECAT_URL = "https://www.pbi.uq.edu.au/clientservices/SECaT/embedChart.aspx"


semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


def _extract_secat_questions(html: str, course_code: str) -> list[SecatQuestion]:  # noqa: C901
    """Extract the question info from the secats."""
    """Extracts SECaT question distributions from the embedded JS."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.select_one("#SECATControl script")

    if not script or "courseSECATData" not in script.text or script.string is None:
        log.warning(f"No SECaT data found for {course_code}")
        return []

    match = re.search(r"var courseSECATData\s*=\s*(\[.*?\]);", script.string, re.DOTALL)
    if not match:
        log.warning(f"Couldn't parse SECaT data for {course_code}")
        return []

    raw_json = match.group(1)

    # clean trailing commas
    cleaned = re.sub(r",\s*}", "}", raw_json)
    cleaned = re.sub(r",\s*]", "]", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        log.exception(f"Failed to decode SECaT JSON for {course_code}")
        return []

    # Group by question
    grouped: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "s_agree": 0.0,
            "agree": 0.0,
            "middle": 0.0,
            "disagree": 0.0,
            "s_disagree": 0.0,
        }
    )

    for row in data:
        if row["COURSE_CD"] != course_code:
            continue

        qname = row["QUESTION_NAME"]

        # Map answers into categories
        answer = row["ANSWER"].lower()
        percent = row["PERCENT_ANSWER"]

        if "strongly agree" in answer:
            grouped[qname]["s_agree"] += percent
        elif answer.startswith("2 agree"):
            grouped[qname]["agree"] += percent
        elif "neither" in answer or "neutral" in answer or "3" in answer:
            grouped[qname]["middle"] += percent
        elif answer.startswith("4 disagree"):
            grouped[qname]["disagree"] += percent
        elif "strongly disagree" in answer:
            grouped[qname]["s_disagree"] += percent

    return [
        SecatQuestion(
            name=qname,
            s_agree=vals["s_agree"],
            agree=vals["agree"],
            middle=vals["middle"],
            disagree=vals["disagree"],
            s_disagree=vals["s_disagree"],
        )
        for qname, vals in grouped.items()
    ]


async def iter_secat_info() -> AsyncGenerator[tuple[str, CourseSecatInfo]]:
    """Extracts course info from the secat, mapping a course code to the secat info."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SECAT_URL)

        letters = page.locator(".rtsLevel1 .rtsLink .rtsTxt")

        # this is getting A, B, C, etc.
        for i in range(await letters.count()):
            letter_elem = letters.nth(i)
            letter_text = await letter_elem.inner_text()
            log.info(f"[Level 1] Clicking letter: {letter_text}")

            await letter_elem.click()

            await page.wait_for_selector(".rtsLevel2 .rtsLink .rtsTxt", state="visible")
            courses_lvl2 = page.locator(".rtsLevel2 .rtsLink .rtsTxt")

            await page.wait_for_selector(".rtsLevel3 .rtsLink .rtsTxt")
            courses_lvl3_texts = await page.locator(".rtsLevel3 .rtsLink .rtsTxt").all_inner_texts()
            log.info(f"Letter {letter_text} has {len(courses_lvl3_texts)} Level 3 courses")

            current_prefix = None

            for full_course_code in courses_lvl3_texts:
                prefix = "".join([c for c in full_course_code if not c.isdigit()])  # e.g., 'ABTS'

                if prefix != current_prefix:
                    # find and click the matching Level 2 element
                    lvl2_elem = courses_lvl2.filter(has_text=prefix)
                    log.info(f"Switching Level 2 to {prefix}")

                    await lvl2_elem.scroll_into_view_if_needed()
                    await lvl2_elem.click(force=True)  # force click in case of overlay
                    current_prefix = prefix

                    await page.wait_for_selector(".rtsLevel3 .rtsLink .rtsTxt")
                    courses_lvl3_texts_for_prefix = await page.locator(".rtsLevel3 .rtsLink .rtsTxt").all_inner_texts()
                    log.info(f"Level 3 courses for {prefix}: {len(courses_lvl3_texts_for_prefix)}")

                # re-locate the Level 3 element to avoid stale element
                course_elem = page.locator(".rtsLevel3 .rtsLink .rtsTxt", has_text=full_course_code)
                log.info(f"[Level 3] Clicking full course: {full_course_code}")
                await course_elem.scroll_into_view_if_needed()
                await course_elem.click()

                await page.wait_for_selector("#lblNoEnrolled")
                enrolled = int(await page.locator("#lblNoEnrolled").inner_text())
                responses = int(await page.locator("#lblNoResponses").inner_text())
                rate = float((await page.locator("#lblRespRate").inner_text()).replace("%", ""))

                html = await page.content()
                questions = _extract_secat_questions(html, full_course_code)

                yield (
                    full_course_code,
                    CourseSecatInfo(
                        num_enrolled=enrolled, num_responses=responses, response_rate=rate, questions=questions
                    ),
                )

        await browser.close()


def _extract_course_html(html: str, course_code: str) -> Course | None:  # noqa: C901, PLR0915
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

            profile_link_tag = row.select_one(".course-offering-profile a")

            profile_url = None
            if profile_link_tag:
                profile_url = str(profile_link_tag.get("href"))
            else:
                log.warning(f"{course_code} profile unavailable for {sem_tag.text.strip()} ({table_id})")

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
        faculty_url=str(faculty_url) if faculty_url else None,
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

    if isinstance(container, bs4.PageElement):
        log.warning("WEIRD -> Its a page element")
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

            log.error(f"Couldn't get data for the following courses: '{', '.join(skipped)}'")

        except Exception:
            log.exception("Error fetching courses")
            raise

        else:
            return courses
