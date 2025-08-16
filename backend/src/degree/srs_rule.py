from serde import serde
from degree.validate_result import ValidateResult, Status


@serde
class SR:
    def validate(plan) -> ValidateResult:
        return ValidateResult(Status.OK, None, "", [])


@serde
class SR1(SR):
    """Complete [N] units for ALL of the following"""

    n: int


@serde
class SR2(SR):
    """Complete [N] to [M] units for ALL of the following"""

    n: int
    m: int


@serde
class SR3(SR):
    """Complete at least [N] units from the following"""

    n: int


@serde
class SR4(SR):
    """Complete [N] to [M] units from the following"""

    n: int
    m: int


@serde
class SR5(SR):
    """Complete exactly [N] units from the following"""

    n: int


@serde
class SR6(SR):
    """Complete one [PLANTYPE] from the following"""

    # plan_type:


@serde
class SR7(SR):
    """Complete exactly [N] [PLANTYPES] from the following"""

    n: int

    # plan_types:


@serde
class SR8(SR):
    """Complete [N] to [M] [PLANTYPES] from the following"""

    n: int
    m: int
    # plan_types:
