"""Course prereqs / degree requirements module."""

import logging

from lark import Lark, Token, Transformer
from lark.exceptions import LarkError

from common.enums import CourseRequirementKind
from common.schemas import UQRoadmapBase

log = logging.getLogger(__name__)

GRAMMAR = r"""
    ?start: expr

    ?expr: term
         | expr OR term          -> or_expr

    ?term: factor
         | term AND factor       -> and_expr
         | course_list           -> and_expr

    ?factor: identifier          -> identifier
           | "(" expr ")"        -> parentheses

    identifier: PART_PATTERN
              | COURSE_CODE

    course_list: COURSE_CODE ("," COURSE_CODE)+

    // Keywords first (avoid tie with COURSE_CODE)
    OR: /or/i
    AND: /and/i

    // Accept "Part B", "Part B.1", "Part B.3.1", etc.
    PART_PATTERN: /Part\s+[A-Za-z](?:\.\d+)*/

    // Avoid swallowing "or"/"and" as course codes
    COURSE_CODE: /(?!or\b)(?!and\b)[A-Za-z0-9]+/i

    %import common.WS
    %ignore WS
"""

parser = Lark(GRAMMAR)


class RequirementRead[T](UQRoadmapBase):
    """Requirement base class."""

    kind: CourseRequirementKind
    value: T


class OrRequirement(RequirementRead[list[RequirementRead]]):
    """OR course requirement."""

    kind: CourseRequirementKind = CourseRequirementKind.OR
    value: list[RequirementRead]


class AndRequirement(RequirementRead[list[RequirementRead]]):
    """And course requirement."""

    kind: CourseRequirementKind = CourseRequirementKind.AND
    value: list[RequirementRead]


class AtomicRequirement(RequirementRead[str]):
    """Atomic course requirement."""

    kind: CourseRequirementKind = CourseRequirementKind.ATOMIC
    value: str


class OtherRequirement(RequirementRead[str]):
    """Other course requirement that normally denotes data that cannot be parsed."""

    kind: CourseRequirementKind = CourseRequirementKind.OTHER
    value: str


# Transformer adapted to work with your requirement models
class RequirementTransformer(Transformer):
    """Transform a requirement string to something with structure."""

    def identifier(self, items: list[Token]) -> AtomicRequirement:
        """Convert identifier to atomic requirement."""
        token_value = items[0].value if hasattr(items[0], "value") else str(items[0])
        return AtomicRequirement(value=token_value)

    def and_expr(self, items: list[Token | RequirementRead]) -> RequirementRead:
        """Handle AND expressions - binary operation."""
        # Collect items, flattening same-type operations
        children = [child for child in items if isinstance(child, RequirementRead)]

        if len(children) == 1:
            return children[0]
        return AndRequirement(value=children)

    def or_expr(self, items: list[Token | RequirementRead]) -> RequirementRead:
        """Handle OR expressions - binary operation."""
        children = [child for child in items if isinstance(child, RequirementRead)]

        if len(children) == 1:
            return children[0]
        return OrRequirement(value=children)

    def parentheses(self, items: list) -> RequirementRead:
        """Handle parentheses - just pass through the expression."""
        return items[0]


# Create the parser
parser = Lark(GRAMMAR)


def parse_requirement(text: str) -> RequirementRead:
    """Parse a requirements string and turn it into something structured."""
    try:
        tree = parser.parse(text)
        return RequirementTransformer().transform(tree)
    except LarkError:
        log.warning(f"Couldn't parse requirements - {text}")
        return OtherRequirement(value=text)
