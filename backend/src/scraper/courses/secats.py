"""Scraping secats."""

import json
import logging
import re
from collections import defaultdict
from collections.abc import AsyncGenerator

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from common.schemas import SecatInfo, SecatQuestion

log = logging.getLogger(__name__)
# Urls
SECAT_URL = "https://www.pbi.uq.edu.au/clientservices/SECaT/embedChart.aspx"


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


async def iter_secat_info() -> AsyncGenerator[tuple[str, SecatInfo]]:
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
                    SecatInfo(num_enrolled=enrolled, num_responses=responses, response_rate=rate, questions=questions),
                )

        await browser.close()
