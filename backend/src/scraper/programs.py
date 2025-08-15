"""Programs scraping."""

import asyncio

import httpx
from bs4 import BeautifulSoup

from scraper.models import Program

HEADERS = {"User-Agent": "Mozilla/5.0"}
PROGRAMS_URL = "https://study.uq.edu.au/study-options/programs"
PROGRAMS_PREFIX = "https://study.uq.edu.au"
PROGRAMS_NUM_PAGES = 11


def extract_programs(html: str) -> list[Program]:
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


async def fetch_page(client: httpx.AsyncClient, page: int) -> list[Program]:
    try:
        response = await client.get(PROGRAMS_URL, params={"page": page})
        response.raise_for_status()
        return extract_programs(response.text)
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return []


async def scrape_all_programs() -> list[Program]:
    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        tasks = [fetch_page(client, page) for page in range(PROGRAMS_NUM_PAGES)]
        all_results = await asyncio.gather(*tasks)

    all_programs = [program for page_programs in all_results for program in page_programs]
    return all_programs
