import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncConnection

from database.session import DatabaseSessionManager
from database.tables import create_tables
from models import Base


@pytest.mark.asyncio
async def test_create_tables() -> None:
    # Setup
    DATABASE_URL = (
        "postgresql+asyncpg://postgres:strongpassword@localhost:5431/postgres"
    )
    test_manager = DatabaseSessionManager(DATABASE_URL)

    # Teardown
    async with test_manager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Run the function
    await create_tables(test_manager)

    async with test_manager.connect() as conn:

        def check_tables(sync_conn: AsyncConnection):
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            assert "fct_refills" in tables
            assert "dim_brands" in tables
            assert "dim_octanes" in tables
            assert "users" in tables

        await conn.run_sync(check_tables)
