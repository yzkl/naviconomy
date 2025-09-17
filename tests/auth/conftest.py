from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth.routes import auth_router
from database.session import get_db_session
from models import Base

# Set up test objects
TEST_DATA = {
    "username": "test-user",
    "email": "email@email.com",
    "password": "strongpassword",
}
TEST_DATA["token_payload"] = {"sub": TEST_DATA["username"]}
TEST_DATA["register_payload"] = {
    "username": TEST_DATA["username"],
    "email": TEST_DATA["email"],
    "password": "weakpassword",
}

# Set up test app
test_app = FastAPI()
test_app.include_router(auth_router)


@pytest.fixture
def testing_data() -> dict:
    return TEST_DATA.copy()


# Set up database
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
