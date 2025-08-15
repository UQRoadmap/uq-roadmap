import argparse
import asyncio
import json
from enum import Enum

# from loguru import logger

from uqscraper.courses import scrape_all_courses
from uqscraper.models import UQScrapeModel
from uqscraper.programs import scrape_all_programs


class ScrapeType(Enum):
    PROGRAM = "program"
    COURSE = "course"


def main():
    parser = argparse.ArgumentParser(description="UQ Scraper CLI")
    parser.add_argument(
        "mode",
        type=ScrapeType,
        choices=list(ScrapeType),
        help="Choose what to scrape: degrees or courses",
    )
    parser.add_argument(
        "--output",
        default="uq_data.json",
        help="Output JSON file (default: uq_data.json)",
    )
    args = parser.parse_args()

    data: list[UQScrapeModel] = []

    if args.mode == ScrapeType.PROGRAM:
        data = asyncio.run(scrape_all_programs())
        # logger.info("Scraped {} programs.", len(data))
    elif args.mode == ScrapeType.COURSE:
        data = asyncio.run(scrape_all_courses())
        # logger.info("Scraped {} courses.", len(data))
    else:
        raise ValueError("Invalid scrape mode selected.")

    output_file = args.output or "uq_data.json"
    with open(output_file, "w") as f:
        json.dump([d.model_dump(mode="json") for d in data], f, indent=2)


if __name__ == "__main__":
    main()
