"""Degree services."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.degree.models import DegreeDBModel
from api.degree.schemas import DegreeSummary


async def get_all_degrees(session: AsyncSession) -> list[DegreeDBModel]:
    """Get all degrees from the db."""
    result = await session.execute(select(DegreeDBModel))
    return list(result.scalars().all())


async def get_degree(session: AsyncSession, degree_code: str, year: int) -> DegreeDBModel | None:
    """Get a degree by its ID."""
    query = select(DegreeDBModel).where(DegreeDBModel.degree_code == degree_code).where(DegreeDBModel.year == year)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_degree_by_id(session: AsyncSession, degree_id: UUID) -> DegreeDBModel | None:
    """Get a degree by its ID."""
    return await session.get(DegreeDBModel, degree_id)


async def get_degrees_summary(session: AsyncSession) -> list[DegreeSummary]:
    """Get summary."""
    stmt = (
        select(DegreeDBModel.degree_code, DegreeDBModel.title, func.array_agg(DegreeDBModel.year).label("years"))
        .group_by(DegreeDBModel.degree_code, DegreeDBModel.title)
        .order_by(DegreeDBModel.title)
    )

    result = (await session.execute(stmt)).all()

    return [
        DegreeSummary(degree_code=row.degree_code, title=row.title, years=row.years)
        for row in result
        if row.title != row.degree_code
    ]
