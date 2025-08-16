"""Course service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.courses.models import CourseDBModel
from common.enums import CourseLevel


async def get_all_courses(
    db: AsyncSession,
    course_category: str | None,
    course_level: CourseLevel | None,
    num_units: int | None,
    is_active: bool | None,  # noqa: FBT001
) -> list[CourseDBModel]:
    """Get all the courses with optional filters.

    Args:
        db (AsyncSession): Database session.
        course_category (str | None): Course category filter.
        course_level (CourseLevel | None): Course level filter.
        num_units (int | None): Number of units filter.
        is_active (bool | None): Active status filter.

    Returns:
        list[CourseDBModel]: _description_
    """
    query = select(CourseDBModel)
    if course_category:
        query = query.where(CourseDBModel.category == course_category)
    if course_level:
        query = query.where(CourseDBModel.level == course_level)
    if num_units:
        query = query.where(CourseDBModel.num_units == num_units)
    if is_active is not None:
        query = query.where(CourseDBModel.active == is_active)

    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_course_by_code(db: AsyncSession, course_code: str) -> CourseDBModel | None:
    """Get a course by code.

    Args:
        db (AsyncSession): Database session.
        course_code (str): Course code to search for.

    Returns:
        CourseDBModel | None: Course model if found, else None.
    """
    result = await db.execute(
        select(CourseDBModel)
        .options(selectinload(CourseDBModel.offerings))  # eagerly load offerings
        .where(CourseDBModel.full_code == course_code)
    )
    return result.unique().scalar_one_or_none()
