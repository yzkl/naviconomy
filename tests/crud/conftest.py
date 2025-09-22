from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from models import Base

DATABASE_URL = "postgresql+asyncpg://postgres:strongpassword@localhost:5431/postgres"


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def testing_session(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        # ✅ Reset sequences so IDs always start from 1
        for table in Base.metadata.tables.values():
            if table.name != "users":
                seq = f"{table.name}_id_seq"
                await conn.execute(text(f'ALTER SEQUENCE "{seq}" RESTART WITH 1'))

    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
