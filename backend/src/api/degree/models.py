"""Degree db models."""

from uuid import UUID, uuid4

from sqlalchemy import JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from api.database.base import BaseDBModel


class DegreeDBModel(BaseDBModel):
    """DB Model for representing degrees."""

    __tablename__ = "degree"
    __table_args__ = (UniqueConstraint("degree_code", "year"),)

    degree_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    degree_code: Mapped[str] = mapped_column()
    year: Mapped[int] = mapped_column()

    title: Mapped[str]
    degree_url: Mapped[str]
    details: Mapped[dict] = mapped_column(JSON)
