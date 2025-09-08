from models import Base

from .session import DatabaseSessionManager


async def create_tables(sessionmanager: DatabaseSessionManager) -> None:
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
