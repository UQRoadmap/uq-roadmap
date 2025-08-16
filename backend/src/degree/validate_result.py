from enum import Enum


class Status(Enum):
    OK = 0
    WARN = 1
    ERROR = 2


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
