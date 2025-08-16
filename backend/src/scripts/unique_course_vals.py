"""Script to get unique offering modes."""

from collections import defaultdict
from pprint import pprint

from scripts.utils import load_courses


def get_unique_fields() -> dict[str, set[str]]:
    """Get all the unique modes."""
    result: dict[str, set[str]] = defaultdict(set)
    courses = load_courses()

    for course in courses:
        result["attendance_mode"].add(course.attendance_mode)
        for offering in course.current_offerings:
            result["modes"].add(offering.mode)
            result["locations"].add(offering.location)
            result["semesters"].add(offering.semester)

        for offering in course.archived_offerings:
            result["modes"].add(offering.mode)
            result["locations"].add(offering.location)
            result["semesters"].add(offering.semester)

    return result


if __name__ == "__main__":
    pprint(get_unique_fields())
