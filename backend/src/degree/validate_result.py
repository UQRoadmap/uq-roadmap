from enum import Enum

from serde import serde


class Status(Enum):
    OK = 0
    WARN = 1
    ERROR = 2


@serde
class ValidateResult:
    status: Status
    percentage: float | None | int
    message: str
    relevant: list[str]

    def __init__(self, status: Status, percentage: float | None | int, message: str, relevant: list[str]):
        self.status = status
        self.percentage = percentage
        self.message = message
        self.relevant = relevant
