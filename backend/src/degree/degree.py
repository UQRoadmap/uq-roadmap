"""Degree requirements representation."""

from collections.abc import Awaitable, Callable
from pprint import pprint

from serde import serde
from serde.json import from_dict

from api.course.models import CourseDBModel
from api.degree.models import DegreeDBModel
from api.plan.plan import Plan
from common.reqs_parsing import CourseRequirementKind, RequirementRead, parse_requirement
from degree.aux_rule import AR
from degree.sr_rule import SR
from degree.validate_result import Status, ValidateResult

CourseCallback = Callable[[str], Awaitable[CourseDBModel | None]]
DegreeCallback = Callable[[str, int], Awaitable[DegreeDBModel | None]]


class PartTree:
    # e.g. A,  A.1, A.1.4.2, A.10, B.1.1.1.2 or A.2.B for specialisation
    part: str
    rules: list[AR | SR]
    children: dict[str, "PartTree"]
    course_getter: CourseCallback
    degree_getter: DegreeCallback

    def __init__(
        self,
        part: str,
        rules: list[AR | SR],
        children: dict[str, list["PartTree"]],
        course_getter: CourseCallback,
        degree_getter: DegreeCallback,
    ):
        self.part = part
        self.rules = rules
        self.children = children
        self.course_getter = course_getter
        self.degree_getter = degree_getter

    def insert(self, part: str, rule: AR | SR):
        # Insert at this node if exact match
        if self.part == part:
            self.rules.append(rule)
            return

        # Only descend if we're an ancestor, e.g. A.1.2 is ancestor for A.1.2.3.4.5
        if self.part:
            if not part.startswith(self.part + "."):
                return
            prefix_len = len(self.part.split("."))
        else:
            prefix_len = 0

        # Compute the immediate child key: self.part plus the next segment from inserted part
        tokens = part.split(".")
        if prefix_len >= len(tokens):
            # IMPOSSIBLE
            return

        child_key = ".".join(tokens[: prefix_len + 1])

        if child_key not in self.children:
            self.children[child_key] = PartTree(child_key, [], {}, self.course_getter, self.degree_getter)

        self.children[child_key].insert(part, rule)

    def evaluate(self, part: str, plan: Plan) -> list[ValidateResult]:
        results = []
        if self.part == part:
            for rule in self.rules:
                results.append(rule.validate(plan, self.course_getter, self.degree_getter))

        if part.startswith(self.part):
            for child in self.children.values():
                results.extend(child.evaluate(part, plan))

        return results

    def evaluate_recursive(self, part: str, plan: Plan) -> list[ValidateResult]:
        results = []
        if self.part.startswith(part):
            for rule in self.rules:
                results.append(rule.validate(plan, self.course_getter, self.degree_getter))

        if part.startswith(self.part + "."):
            for child in self.children.values():
                results.extend(child.evaluate(part, plan))

        return results

    def evaluate_requirement(self, requirements: RequirementRead, plan: Plan, prefix: str) -> list[ValidateResult]:
        results = []
        if requirements.kind == CourseRequirementKind.OR:
            flag = True
            temp_results = []
            for child in requirements.value:
                flag2 = True
                intermediate = self.evaluate_requirement(child, plan, prefix)
                for result in intermediate:
                    if result.status != Status.OK:
                        flag2 = False
                if flag2:
                    flag = False
                temp_results.extend(intermediate)
            if flag:
                results.extend(temp_results)
                results.append(ValidateResult(Status.ERROR, None, "", [], self.part))
        elif requirements.kind == CourseRequirementKind.AND:
            for child in requirements.value:
                results.extend(self.evaluate_requirement(child, plan, prefix))
        elif requirements.kind == CourseRequirementKind.ATOMIC:
            requirements.value = requirements.value.removeprefix("Part ")
            results.extend(self.evaluate(((prefix + ".") if prefix != "" else "") + requirements.value, plan))

        return results


@serde
class Degree:
    name: str
    code: str
    year: str
    sem: int
    part: str | None

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

    def prefix(self, prefix: str):
        self.part_references = {(prefix + "." + key): val for key, val in self.part_references.items()}
        for ar in self.aux:
            ar.part = prefix + "." + ar.part
        for sr in self.srs:
            sr.part = prefix + "." + sr.part

    async def validate(
        self, plan: Plan, course_getter: CourseCallback, degree_getter: DegreeCallback
    ) -> list[ValidateResult]:
        tree = PartTree("", [], {}, course_getter, degree_getter)
        for aux in self.aux:
            tree.insert(aux.part, aux)
        for srs in self.srs:
            tree.insert(srs.part, srs)

        if self.part is None:
            self.part = ""

        results: list[ValidateResult] = []
        for rule in self.rule_logic:
            requirements = parse_requirement(rule)
            results.extend(tree.evaluate_requirement(requirements, plan, self.part))

        if len(self.rule_logic) == 0:
            for srs in self.srs:
                results.extend(tree.evaluate(srs.part, plan))
            for aux in self.aux:
                results.extend(tree.evaluate(aux.part, plan))

        # Validate sub-degrees :)
        for prefix, specs in plan.specialisations.items():
            if self.part is None:
                self.part = ""

            if not prefix.startswith(self.part):
                continue

            for spec_code in specs:
                dbm = await degree_getter(str(spec_code), int(self.year))
                sub_degree: Degree = from_dict(Degree, dbm.details)
                sub_degree.part = ((self.part + ".") if self.part != "" else "") + prefix
                sub_degree.prefix(prefix)
                sub_results = await sub_degree.validate(plan, course_getter, degree_getter)
                pprint(sub_degree)
                pprint(plan)
                pprint(sub_results)
                results.extend(sub_results)

        return results

    @staticmethod
    def build() -> "Degree":
        return Degree(
            part="",
            name="",
            code="",
            year="",
            sem=1,
            aux=list(),
            srs=list(),
            part_references=dict(),
            rule_logic=list(),
        )
