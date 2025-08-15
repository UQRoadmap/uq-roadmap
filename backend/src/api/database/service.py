"""Database services."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.config import CONFIG

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


async def initialise_database(engine: AsyncEngine) -> None:
    """Initialise database."""
    # Importing as now sqlalchemy will know about them when creating the schema
    from api.database.base import BaseDBModel

    async with engine.begin() as conn:
        await conn.run_sync(BaseDBModel.metadata.create_all)

    log.info("Initialising database was successful.")
