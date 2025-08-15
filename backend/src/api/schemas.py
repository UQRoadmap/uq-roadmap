"""Base schema."""

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
