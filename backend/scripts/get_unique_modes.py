from pathlib import Path

import orjson

COURSES_FILE = "data/courses.json"


def get_unique_modes() -> set[str]:
    """Get all the unique modes."""
    result: set[str] = set()
    with Path.open(Path(COURSES_FILE), "rb") as f:
        data = orjson.loads(f.read())

        for course in data["courses"]:
            current_modes = {o["mode"] for o in course["current_offerings"]}
            archived_modes = {o["mode"] for o in course["archived_offerings"]}
            result = result.union(current_modes).union(archived_modes)

    return result


if __name__ == "__main__":
    print(get_unique_modes())
