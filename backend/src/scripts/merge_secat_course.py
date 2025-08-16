"""Merge secat course script."""

from pathlib import Path

import orjson

from scripts.constants import MERGED_COURSES_FILE_NAME
from scripts.utils import load_courses, load_secats


def main() -> None:
    """Main function."""
    courses = load_courses()
    secats = load_secats()

    for course in courses:
        secat = secats.get(course.code, None)
        if secat is None:
            continue
        course.secat = secat

    with Path.open(Path(MERGED_COURSES_FILE_NAME), "wb") as f:
        data = {"courses": [c.model_dump(mode="json") for c in courses]}
        output = orjson.dumps(data, option=orjson.OPT_INDENT_2)
        f.write(output)


if __name__ == "__main__":
    main()
