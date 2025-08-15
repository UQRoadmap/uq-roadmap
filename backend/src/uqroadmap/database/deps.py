"""Database dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends

from uqroadmap.database.service import AsyncSession, get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]
