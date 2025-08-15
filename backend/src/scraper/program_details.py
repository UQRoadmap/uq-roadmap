from bs4 import BeautifulSoup
import cloudscraper
import json
import re

DETAILS_URL = "https://programs-courses.uq.edu.au/requirements/program/{}/{}"


def extract_details(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Find the <div id="main-content">
    main_content = soup.find("div", id="main-content")
    if not main_content:
        return None

    # Find the first <script type="text/javascript"> inside main-content
    script_tag = main_content.find("script", type="text/javascript")
    if not script_tag:
        return None

    # Get the script's content
    script_content = script_tag.string.strip()
    match = re.search(r'window\.AppData\s*=\s*({.*?});?\s*$', script_content, re.DOTALL)
    if not match:
        return None
    json_str = match.group(1)
    # Remove trailing semicolon if present
    json_str = json_str.rstrip(';')
    # Parse JSON
    try:
        return json.loads(json_str)
    except Exception as e:
        print("JSON decode error:", e)
        return None
    
    return script_content


def fetch_programs():
    with open("program.json", "r") as f:
        data = json.load(f)
    return list(set([item["program_id"] for item in data]))


def fetch_page(scraper, program_id: int, year: int) -> list:
    try:
        url = DETAILS_URL.format(program_id, year)
        print(url)
        response = scraper.get(url)
        response.raise_for_status()
        return extract_details(response.text)
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return []


def scrape_all_program_details(programs: list[str]) -> list:
    scraper = cloudscraper.create_scraper()
    all_programs = []
    for program_id in programs:
        year_data = {}
        for year in range(2021, 2027):
            details = fetch_page(scraper, program_id, year)
            year_data[str(year)] = details
        all_programs.append({
            "program_id": program_id,
            "data": year_data
        })
    return all_programs


if __name__ == "__main__":
    programs = fetch_programs()
    details = scrape_all_program_details(programs)
    with open("program_details.json", "w") as f:
        json.dump(details, f, indent=2)
