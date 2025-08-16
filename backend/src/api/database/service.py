"""Database services."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import Connection, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.config import CONFIG
from api.database.seed import seed_db

log = logging.getLogger(__name__)

db_engine: AsyncEngine = create_async_engine(
    CONFIG.db_url,
    pool_pre_ping=True,
)
session_factory = async_sessionmaker(
    db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Get generator to get database session.

    :return: generator for async db session.
    :rtype: AsyncGenerator[AsyncSession, None]
    :yield: db session generator.
    :rtype: Iterator[AsyncGenerator[AsyncSession, None]]
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            log.exception("Database error occurred")
            await session.rollback()
            await session.close()
            raise


async def setup_database(engine: AsyncEngine) -> None:
    """Initialise database."""
    # Importing as now sqlalchemy will know about them when creating the schema
    from api.courses.models import CourseDBModel, CourseOfferingDBModel, CourseSecatDBModel, CourseSecatQuestionsDBModel
    from api.database.base import BaseDBModel
    from api.degree.models import DegreeDBModel

    course_table_exists: bool = True
    degree_table_exists: bool = True

    async with engine.begin() as conn:

        def check_tables(sync_conn: Connection) -> tuple[bool, bool]:
            inspector = inspect(sync_conn)
            course_exists = inspector.has_table(CourseDBModel.__tablename__)
            degree_exists = inspector.has_table(DegreeDBModel.__tablename__)
            return course_exists, degree_exists

        course_table_exists, degree_table_exists = await conn.run_sync(check_tables)

        await conn.run_sync(BaseDBModel.metadata.create_all)

    log.info("Initialising database was successful.")

    async for session in get_db():
        await seed_db(session, not course_table_exists, not degree_table_exists)
