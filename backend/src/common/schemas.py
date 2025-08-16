"""Base schemas."""

import datetime as dt

from pydantic import BaseModel, ConfigDict


# Serialize datetime values to local format
def _serialize_datetime(v: dt.datetime) -> str:
    v = v.astimezone(tz=None)
    return v.strftime("%Y-%m-%dT%H:%M:%SZ")


class UQRoadmapBase(BaseModel):
    """Base pydantic schema."""

    model_config = ConfigDict(
        json_encoders={
            dt.datetime: _serialize_datetime,
        },
        from_attributes=True,
    )


class AssessmentItem(UQRoadmapBase):
    """Scraped assessment info."""

    task: str
    category: str | None = None
    description: str | None = None
    weight: float | None = None
    due_date: str | None = None
    mode: str | None = None
    learning_outcomes: list[str]

    # Flags
    hurdle: bool
    identity_verified: bool


class SecatQuestion(UQRoadmapBase):
    """Secat question."""

    name: str
    s_agree: float
    agree: float
    middle: float
    disagree: float
    s_disagree: float


class SecatInfo(UQRoadmapBase):
    """Secat information for a course."""

    num_enrolled: int
    num_responses: int
    response_rate: float
    questions: list[SecatQuestion]
