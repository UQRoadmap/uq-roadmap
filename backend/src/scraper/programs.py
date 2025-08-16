"""Programs scraping."""

import logging

import curl_cffi
from bs4 import BeautifulSoup

from scraper.models import Program

HEADERS = {"User-Agent": "Mozilla/5.0"}
PROGRAMS_URL = "https://study.uq.edu.au/study-options/programs"
PROGRAMS_PREFIX = "https://study.uq.edu.au"
PROGRAMS_NUM_PAGES = 11

log = logging.getLogger(__name__)


def _extract_programs(html: str) -> list[Program]:
    soup = BeautifulSoup(html, "html.parser")
    program_cards = soup.select("div.grid__col")
    programs = []

    for card in program_cards:
        link = card.select_one("a.card__link")
        title_super = card.select_one("span.card__title__super")
        title_main = card.select_one("h3.card__title")

        if not link or not title_main:
            continue

        href = link["href"]
        full_url = PROGRAMS_PREFIX + href
        program_id = href.strip("/").split("-")[-1]

        if not program_id.isdigit():
            continue

        super_text = title_super.get_text(strip=True) if title_super else ""
        full_title = f"{super_text} {link.get_text(strip=True)}".strip()

        programs.append(Program(title=full_title, url=full_url, program_id=program_id))

    return programs


async def _fetch_page(session: curl_cffi.AsyncSession, page: int) -> list[Program]:
    try:
        response = await session.get(PROGRAMS_URL, params={"page": page}, headers=HEADERS)
        response.raise_for_status()
        return _extract_programs(response.text)
    except Exception:
        log.exception(f"Error fetching page {page}")
        return []


async def scrape_all_programs() -> list[Program]:
    """Scrape all programs."""
    all_programs: list[Program] = []

    async with curl_cffi.AsyncSession() as session:
        for page in range(PROGRAMS_NUM_PAGES):
            page_programs = await _fetch_page(session, page)
            all_programs.extend(page_programs)
    return all_programs
