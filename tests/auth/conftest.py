from typing import AsyncGenerator

import pytest
import pytest_asyncio
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from models import Base

# Set up test objects
TEST_DATA = {
    "username": "test-user",
    "email": "email@email.com",
    "password": SecretStr("strongpassword"),
}
TEST_DATA["token_payload"] = {"sub": TEST_DATA["username"]}
TEST_DATA["register_payload"] = {
    "username": TEST_DATA["username"],
    "email": TEST_DATA["email"],
    "password": "weakpassword",
}


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
