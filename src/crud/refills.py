from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityDoesNotExistError
from schemas import Refill, RefillCreate, RefillUpdate


async def create_refill(params: RefillCreate, session: AsyncSession) -> Refill:
    db_refill = models.Refill(**params.model_dump())
    session.add(db_refill)
    await session.commit()
    await session.refresh(db_refill)
    return Refill.model_validate(db_refill)


async def find_refill(id: int, session: AsyncSession) -> models.Refill:
    db_refill = await session.get(models.Refill, id)
    if not db_refill:
        raise EntityDoesNotExistError(f"Refill with id {id} does not exist.")
    return db_refill


async def find_refills(session: AsyncSession) -> List[models.Refill]:
    stmt = select(models.Refill).order_by(models.Refill.id)
    db_refills = (await session.scalars(stmt)).all()
    return db_refills


async def read_refill(id: int, session: AsyncSession) -> Refill:
    db_refill = await find_refill(id, session)
    return Refill.model_validate(db_refill)


async def read_refills(session: AsyncSession) -> List[Refill]:
    db_refills = await find_refills(session)
    return [Refill.model_validate(db_refill) for db_refill in db_refills]


async def update_refill(id: int, params: RefillUpdate, session: AsyncSession) -> Refill:
    db_refill = find_refill(id, session)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_refill, attr, value)
    session.add(db_refill)
    await session.commit()
    await session.refresh(db_refill)
    return Refill.model_validate(db_refill)


async def delete_refill(id: int, session: AsyncSession) -> Refill:
    db_refill = find_refill(id, session)
    await session.delete(db_refill)
    await session.commit()
    return Refill.model_validate(db_refill)
