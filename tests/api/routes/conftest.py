from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.routes import brands, octanes, refills
from database.session import get_db_session
from models import Base

# Set up test app
test_app = FastAPI()
test_app.include_router(brands.router)
test_app.include_router(octanes.router)
test_app.include_router(refills.router)


DATABASE_URL = "postgresql+asyncpg://postgres:strongpassword@localhost:5431/postgres"


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def testing_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        for table in Base.metadata.tables.values():
            seq = f"{table.name}_id_seq"
            await conn.execute(text(f'ALTER SEQUENCE "{seq}" RESTART WITH 1'))

    async_session = async_sessionmaker(
        bind=engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(
    testing_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield testing_session

    test_app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="https://test"
    ) as client:
        try:
            yield client
        finally:
            test_app.dependency_overrides = {}
