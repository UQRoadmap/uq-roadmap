"""Degree services."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uqroadmap.degree.models import DegreeDBModel
from uqroadmap.degree.schemas import DegreeCreate


async def create_degree(session: AsyncSession, degree_in: DegreeCreate) -> DegreeDBModel:
    """Create a new degree in the db."""
    model = DegreeDBModel(degree_id=degree_in.degree_id, title=degree_in.title)

    session.add(model)
    await session.commit()
    return model


async def get_all_degrees(session: AsyncSession) -> list[DegreeDBModel]:
    """Get all degrees from the db."""
    result = await session.execute(select(DegreeDBModel))
    return list(result.scalars().all())


async def get_degree_by_id(session: AsyncSession, program_id: int) -> DegreeDBModel | None:
    """Get a degree by its ID."""
    return await session.get(DegreeDBModel, program_id)
