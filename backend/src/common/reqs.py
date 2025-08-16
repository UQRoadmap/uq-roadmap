"""Course prereqs / degree requirements module."""

from lark import Lark, Token, Transformer

from common.schemas import UQRoadmapBase

GRAMMAR = """
    ?start: expr

    ?expr: term
         | expr OR term   -> or_expr

    ?term: factor
         | term AND factor -> and_expr

    ?factor: identifier         -> identifier
           | "(" expr ")"   -> parentheses

    identifier: PART_PATTERN
              | COURSE_CODE

    PART_PATTERN: "Part" WS LETTER
    COURSE_CODE: /[a-zA-Z0-9]+/
    LETTER: /[a-zA-Z]/

    OR: /or/i
    AND: /and/i

    %import common.WS
    %ignore WS
"""

parser = Lark(GRAMMAR)


class RequirementRead[T](UQRoadmapBase):
    """Requirement base class."""

    kind: str
    value: T


class OrRequirement(RequirementRead[list[RequirementRead]]):
    """OR course requirement."""

    kind: str = "or"
    value: list[RequirementRead]


class AndRequirement(RequirementRead[list[RequirementRead]]):
    """And course requirement."""

    kind: str = "and"
    value: list[RequirementRead]


class AtomicRequirement(RequirementRead[str]):
    """Atomic course requirement."""

    kind: str = "atomic"
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
    tree = parser.parse(text)
    return RequirementTransformer().transform(tree)
