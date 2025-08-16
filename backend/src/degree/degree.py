"""Degree requirements representation."""

from serde import serde

from api.plan import Plan
from degree.aux_rule import AR
from degree.srs_rule import SR
from degree.validate_result import ValidateResult, Status
from common.reqs_parsing import parse_requirement


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

    def validate(self, plan: Plan) -> list[ValidateResult]:
        results = []
        errored_parts = set()
        for aux in self.aux:
            results.append(aux.validate(plan))
            if results[-1].status == Status.ERROR:
                # An error produced by aux means an error in the part I guess?
                errored_parts.add(results[-1].part)
        for srs in self.srs:
            results.append(srs.validate(plan))
            if results[-1].status == Status.ERROR:
                errored_parts.add(results[-1].part)

        for rule in self.rule_logic:
            parsed = parse_requirement(rule)
            # TODO use this
            pass

        return results

    def __init__(self):
        self.name = ""
        self.code = ""
        self.year = ""
        self.sem = ""
        self.aux = list()
        self.srs = list()
        self.part_references = dict()
        self.rule_logic = list()
