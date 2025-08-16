"""A Complete User Plan."""


class Plan:
    name: str
    # maps (year, sem) to list of chosen courses
    course_dates: dict[tuple[int, int], list[str]]
    course_reqs: dict[str, list[str]]
    courses: list[str]
    degree: str
    specialisations: dict[str, list[str]]

    def __init__(
        self,
        name: str,
        course_dates: dict[tuple[int, int], list[str]],
        course_reqs: dict[str, list[str]],
        courses: list[str],
        degree: str,
        specialisations: dict[str, list[str]],
    ):
        self.name = name
        self.course_dates = course_dates
        self.course_reqs = course_reqs
        self.courses = courses
        self.degree = degree
        self.specialisations = specialisations
