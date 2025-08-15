"""Database base DB Model."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class BaseDBModel(DeclarativeBase, AsyncAttrs):
    """Base database model."""

    def to_dict(self) -> dict[Any, Any]:
        """Return dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
