"""Degree db models."""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from api.database.base import BaseDBModel


class DegreeDBModel(BaseDBModel):
    """DB Model for representing degrees."""

    __tablename__ = "degrees"

    degree_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    json: Mapped[dict] = mapped_column(JSON)
