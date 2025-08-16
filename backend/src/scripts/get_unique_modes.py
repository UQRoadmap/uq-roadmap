"""Script to get unique offering modes."""

from scripts.utils import load_courses


def get_unique_modes() -> set[str]:
    """Get all the unique modes."""
    result: set[str] = set()
    courses = load_courses()

    for course in courses:
        current_modes = {o.mode for o in course.current_offerings}
        archived_modes = {o.mode for o in course.archived_offerings}
        result = result.union(current_modes).union(archived_modes)

    return result


if __name__ == "__main__":
    print(get_unique_modes())  # noqa: T201
