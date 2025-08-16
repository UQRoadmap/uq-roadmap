"""Script to get unique offering modes."""

from pathlib import Path

import orjson

from scripts.constants import COURSES_FILE_NAME


def get_unique_modes() -> set[str]:
    """Get all the unique modes."""
    result: set[str] = set()
    with Path.open(Path(COURSES_FILE_NAME), "rb") as f:
        data = orjson.loads(f.read())

        for course in data["courses"]:
            current_modes = {o["mode"] for o in course["current_offerings"]}
            archived_modes = {o["mode"] for o in course["archived_offerings"]}
            result = result.union(current_modes).union(archived_modes)

    return result


if __name__ == "__main__":
    print(get_unique_modes())
