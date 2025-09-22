from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from database.session import DatabaseSessionManager
from exceptions.exceptions import ServiceError

DATABASE_URL = "postgresql+asyncpg://postgres:strongpassword@localhost:5431/postgres"


@pytest_asyncio.fixture
async def testing_manager() -> AsyncGenerator[DatabaseSessionManager, None]:
    manager = DatabaseSessionManager(DATABASE_URL)
    try:
        yield manager
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_sessionmanager_initializes(
    testing_manager: DatabaseSessionManager,
) -> None:
    assert testing_manager.engine is not None
    assert testing_manager._sessionmaker is not None


@pytest.mark.asyncio
async def test_sessionmanager_raises_ServiceError_for_invalid_db_url() -> None:
    with pytest.raises(ServiceError):
        DatabaseSessionManager("invalid_url")


@pytest.mark.asyncio
async def test_connect_raises_ServiceError_for_empty_engine(
    testing_manager: DatabaseSessionManager,
) -> None:
    testing_manager.engine = None
    with pytest.raises(ServiceError):
        async with testing_manager.connect():
            pass


@pytest.mark.asyncio
async def test_connect_raises_ServiceError_for_SQLAlchemyError_during_connection(
    testing_manager: DatabaseSessionManager,
) -> None:
    with pytest.raises(ServiceError):
        async with testing_manager.connect() as conn:
            await conn.execute(text("SELECT * FROM"))


@pytest.mark.asyncio
async def test_connect_yields_connections(
    testing_manager: DatabaseSessionManager,
) -> None:
    async with testing_manager.connect() as conn:
        assert isinstance(conn, AsyncConnection)


@pytest.mark.asyncio
async def test_session_raises_ServiceError_for_empty_sessionmaker(
    testing_manager: DatabaseSessionManager,
) -> None:
    testing_manager._sessionmaker = None
    with pytest.raises(ServiceError):
        async with testing_manager.session():
            pass


@pytest.mark.asyncio
async def test_session_raises_ServiceError_for_SQLAlchemyError_during_session(
    testing_manager: DatabaseSessionManager,
) -> None:
    with pytest.raises(ServiceError):
        async with testing_manager.session() as session:
            await session.execute(text("SELECT * FROM"))


@pytest.mark.asyncio
async def test_session_yields_sessions(
    testing_manager: DatabaseSessionManager,
) -> None:
    async with testing_manager.session() as session:
        assert isinstance(session, AsyncSession)
