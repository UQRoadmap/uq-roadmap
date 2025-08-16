"""Main module."""

import argparse
import asyncio
import json
import logging
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from common.enums import LogLevel
from common.logging import configure_logging
from scraper.courses import iter_secat_info, scrape_courses
from scraper.models import Program
from scraper.programs import scrape_all_programs
from scraper.plans import scrape_all_plans, fetch_plans


if TYPE_CHECKING:
    from scraper.courses.models import Course
    from scraper.models import Program


class ScrapeType(Enum):
    """CLI Enum for what type of scraping to do."""

    PROGRAM = "program"
    COURSE = "course"
    SECAT = "secat"
    DETAILS = "details"
    PLANS = "plans"


def main() -> None:
    """Main method."""
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
        help="Output JSON file",
    )
    args = parser.parse_args()
    output_file = args.output

    data: dict = {}

    # getting the programs/degrees
    if args.mode == ScrapeType.PROGRAM:
        programs: list[Program] = scrape_all_programs()
        data = {"programs": [r.model_dump(mode="json") for r in programs]}
        with Path.open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Scraped {len(programs)} programs. Written to {output_file}")
        return

    # getting all the uq courses
    if args.mode == ScrapeType.COURSE:
        courses: list[Course] = asyncio.run(scrape_courses())
        data = {"courses": [c.model_dump(mode="json") for c in courses]}
        with Path.open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Scraped {len(courses)} courses. Written to {output_file}")
        return

    # getting all the secats
    if args.mode == ScrapeType.SECAT:
        count = 0

        async def write_secat(output_file: str) -> None:
            with Path.open(Path(output_file), "w") as f:
                async for course_code, info in iter_secat_info():
                    entry = {"course": course_code, **info.model_dump(mode="json")}
                    f.write(json.dumps(entry) + "\n")
                    nonlocal count
                    count += 1

        asyncio.run(write_secat(output_file))
        log.info(f"Scraped secats for {count} courses. Written to {output_file}")
        return
    
    if args.mode == ScrapeType.PLANS:
        plans = fetch_plans()
        result = scrape_all_plans(plans)
        data = {"plans": [r for r in result if r is not None]}
        log.info(f"Scraped details for {len(data['program_details'])} programs.")

    raise ValueError("Invalid scrape mode selected.")


if __name__ == "__main__":
    main()
