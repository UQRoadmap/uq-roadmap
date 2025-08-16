from bs4 import BeautifulSoup
import cloudscraper
import json
import re

PLAN_URL = "https://programs-courses.uq.edu.au/requirements/plan/{}/{}"


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


def fetch_plans():
    data = []
    with open("plan_codes.txt", "r") as f:
        for line in f:
            line = line.strip()
            data.append(line)
    return list(set(data))


def fetch_page(scraper, plan_id: int, year: int) -> list:
    try:
        url = PLAN_URL.format(plan_id, year)
        response = scraper.get(url)
        response.raise_for_status()
        return extract_details(response.text)
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return []


def scrape_all_plans(plans: list[str]) -> list:
    scraper = cloudscraper.create_scraper()
    all_programs = []
    for plan_id in plans:
        year_data = {}
        for year in range(2021, 2027):
            details = fetch_page(scraper, plan_id, year)
            year_data[str(year)] = details
        all_programs.append({
            "plan_id": plan_id,
            "data": year_data
        })
        print(plan_id)
    return all_programs


if __name__ == "__main__":
    plans = fetch_plans()
    details = scrape_all_plans(plans)
    with open("plans1.json", "w") as f:
        json.dump(details, f, indent=2)