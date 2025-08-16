"""Database mixins module."""

import datetime as dt

from sqlalchemy import DateTime as SQLDatetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    """Timestamp Mixin."""

    created_at: Mapped[dt.datetime] = mapped_column(
        SQLDatetime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        SQLDatetime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        onupdate=lambda: dt.datetime.now(dt.UTC),
    )
