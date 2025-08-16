"""Database dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends

from api.database.service import AsyncSession, get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]
