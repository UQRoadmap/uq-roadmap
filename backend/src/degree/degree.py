"""Degree requirements representation."""

from serde import serde
from degree.aux_rule import AR
from degree.srs_rule import SR


@serde
class Degree:
    name: str
    code: str
    year: str
    sem: int

    # ALL aux rules associated with this course.
    # Aux rules (and SRS) conveniently have a ref, e.g. "A" or "A.1"
    # They can use that when passed the course info
    aux: list[AR]
    srs: list[SR]

    # Categories relevant to this degree.
    # Maps category a/b/c/d etc to its name
    # e.g. "A" -> "MPcompSci 1.5 Year DUration"
    # and  "A.1" -> "MCompSci Flexible Core Courses"
    part_references: dict[str, str]

    # Rule logic that operates broadly on the categories.
    # An entry might be A and B or A.1 OR B.1
    rule_logic: list[str]
