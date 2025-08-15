import argparse
import asyncio
import json
import logging
from enum import Enum

from common.enums import LogLevel
from common.logging import configure_logging
from scraper.courses import scrape_all_courses
from scraper.models import UQScrapeModel
from scraper.programs import scrape_all_programs


class ScrapeType(Enum):
    PROGRAM = "program"
    COURSE = "course"


def main():
    configure_logging(LogLevel.debug)

    log = logging.getLogger(__name__)

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
        log.info(f"Scraped {len(data)} programs.")
    elif args.mode == ScrapeType.COURSE:
        data = asyncio.run(scrape_all_courses())
        log.info(f"Scraped {len(data)} courses.")
    else:
        raise ValueError("Invalid scrape mode selected.")

    output_file = args.output or "uq_data.json"
    with open(output_file, "w") as f:
        json.dump([d.model_dump(mode="json") for d in data], f, indent=2)


if __name__ == "__main__":
    main()
