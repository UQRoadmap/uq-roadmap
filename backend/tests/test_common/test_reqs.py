"""Tests for reqs.py."""

import pytest

from common.reqs import parse_requirement

DATA = [
    "( Part A OR Part B ) AND Part C",
    "(Part A or Part B) and Part C and Part D",
    "A and B",
    "Part A",
    "Part A AND ( Part B OR Part C )",
    "Part A AND ( Part B OR Part C ) AND Part D",
    "Part A AND ( Part B OR Part C ) AND Part D AND Part E",
    "Part A AND ( Part B OR Part C OR ( Part D AND Part E ) )",
    "Part A AND ( Part B OR Part C OR Part D ) AND Part E",
    "Part A AND ( Part B OR Part C OR Part D OR Part E OR Part F OR Part G ) AND "
    "Part H AND Part I AND Part J AND Part K",
    "Part A AND Part B",
    "Part A AND Part B AND ( Part C OR Part D )",
    "Part A AND Part B AND ( Part C OR Part D OR Part E )",
    "Part A AND Part B AND Part C",
    "Part A AND Part B AND Part C AND Part D",
    "Part A AND Part B AND Part C AND Part D AND ( Part E OR Part F )",
    "Part A AND Part B AND Part C AND Part D AND Part E",
    "Part A AND Part B AND Part C AND Part D AND Part E AND Part F",
    "Part A AND Part B AND Part C AND Part D AND Part E AND Part F AND Part G AND Part H",
    "Part A OR Part B",
    "Part A OR Part B OR Part C",
    "Part A OR Part B OR Part C OR Part D",
    "Part A and Part B",
    "Part A and Part B ",
    "Part A and Part B and (Part C or Part D) and Part E",
    "Part A and Part B and Part C",
    "Part A and Part B and Part C ",
    "Part A and Part B and Part C and Part D",
    "Part A and Part B and Part C and Part D and Part E",
    "Part A and Part B and Part C and Part D and Part E and Part F",
    "Part B AND Part A",
]


@pytest.mark.parametrize("requirement_str", DATA)
def test_parse_requirement_no_error(requirement_str: str):
    """Test that parsing each requirement string does not raise an exception."""
    try:
        _ = parse_requirement(requirement_str)
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Parsing failed for: {requirement_str}\nException: {e}")
