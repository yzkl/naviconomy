from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import settings
from exceptions.exceptions import ServiceError

DATABASE_URL = settings.database_url
MAX_CONNECTIONS_COUNT = settings.max_connections_count


class DatabaseSessionManager:
    def __init__(self, host: str, **engine_kwargs):
        try:
            self.engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
            self._sessionmaker: async_sessionmaker[AsyncSession] | None = (
                async_sessionmaker(bind=self.engine, expire_on_commit=False)
            )
        except SQLAlchemyError:
            logger.error("Failed to initialize database engine.")
            raise ServiceError

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            logger.info("Database engine disposed.")
            self.engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            logger.error("Attempted to connect but engine is not initiated.")
            raise ServiceError

        logger.debug("Opening database connection.")
        async with self.engine.begin() as connection:
            try:
                yield connection
            except SQLAlchemyError:
                await connection.rollback()
                logger.error("Error occurred during database connection.")
                raise ServiceError

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            logger.error("Sessionmaker is unavailable.")
            raise ServiceError

        logger.debug("Opening database session.")
        session = self._sessionmaker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            logger.error("Error occurred during database session.")
            raise ServiceError
        finally:
            await session.close()
            logger.info("Database session closed.")


sessionmanager = DatabaseSessionManager(
    DATABASE_URL.get_secret_value(), pool_size=MAX_CONNECTIONS_COUNT
)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
