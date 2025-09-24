from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth.dependencies import get_current_active_user
from auth.models import User
from database.session import get_db_session
from main import app
from models import Base

DATABASE_URL = "postgresql+asyncpg://postgres:strongpassword@localhost:5431/postgres"


TEST_DATA = {
    "brand1": "Petron",
    "brand2": "Shell",
    "octane1": 91,
    "octane2": 95,
    "refill1": {
        "odometer": 123.5,
        "liters_filled": 3.5,
        "brand_id": 1,
        "octane_id": 1,
        "ethanol_percent": 0.1,
        "cost": 175,
    },
    "refill2": {
        "odometer": 456.7,
        "liters_filled": 3.7,
        "brand_id": 2,
        "octane_id": 2,
        "ethanol_percent": 0.12,
        "cost": 200,
    },
    "user": {
        "username": "test-user",
        "email": "email@email.com",
        "password": "pass123",
        "is_active": True,
    },
    "deactivated_user": {
        "username": "x-user",
        "email": "x@email.com",
        "password": "x123",
        "is_active": False,
    },
}


@pytest.fixture
def testing_data() -> dict:
    return TEST_DATA.copy()


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def testing_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        for table in Base.metadata.tables.values():
            if table.name != "users":
                seq = f"{table.name}_id_seq"
                await conn.execute(text(f'ALTER SEQUENCE "{seq}" RESTART WITH 1'))

    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def override_get_current_active_user() -> AsyncGenerator[User, None]:
    yield User(
        username=TEST_DATA["user"]["username"],
        email=TEST_DATA["user"]["email"],
        is_active=TEST_DATA["user"]["is_active"],
    )


@pytest_asyncio.fixture
async def async_client(
    testing_session: AsyncSession, override_get_current_active_user: User
) -> AsyncGenerator[AsyncClient, None]:
    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        yield testing_session

    async def override_user() -> AsyncGenerator[User, None]:
        yield override_get_current_active_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_active_user] = override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        try:
            yield client
        finally:
            app.dependency_overrides = {}
