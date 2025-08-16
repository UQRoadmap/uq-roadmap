from enum import Enum
from serde import serde
from serde.json import to_json, from_json


class Status(Enum):
    OK = 0
    WARN = 1
    ERROR = 2


@serde
class ValidateResult:
    status: Status
    percentage: float | None
    message: str
    relevant: list[str]

    def __init__(self, status, percentage, message, relevant):
        self.status = status
        self.percentage = percentage
        self.message = message
        self.relevant = relevant
