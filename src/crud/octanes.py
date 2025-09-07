from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Octane, OctaneCreate, OctaneUpdate


async def create_octane(params: OctaneCreate, session: AsyncSession) -> Octane:
    db_octane = models.Octane(**params.model_dump())
    session.add(db_octane)
    try:
        await session.commit()
        await session.refresh(db_octane)
    except IntegrityError:
        raise EntityAlreadyExistsError("Octane already exists.")
    return Octane.model_validate(db_octane)


async def find_octane(id: int, session: AsyncSession) -> models.Octane:
    db_octane = await session.get(models.Octane, id)
    if not db_octane:
        raise EntityDoesNotExistError(f"Octane with id {id} does not exist.")
    return db_octane


async def find_octanes(session: AsyncSession) -> List[models.Octane]:
    stmt = select(models.Octane).order_by(models.Octane.id)
    db_octanes = (await session.scalars(stmt)).all()
    return db_octanes


async def read_octane(id: int, session: AsyncSession) -> Octane:
    db_octane = await find_octane(id, session)
    return Octane.model_validate(db_octane)


async def read_octanes(session: AsyncSession) -> List[Octane]:
    db_octanes = await find_octanes(session)
    return [Octane.model_validate(db_octane) for db_octane in db_octanes]


async def update_octane(id: int, params: OctaneUpdate, session: AsyncSession) -> Octane:
    db_octane = await find_octane(id, session)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_octane, attr, value)
    session.add(db_octane)
    try:
        await session.commit()
        await session.refresh(db_octane)
    except IntegrityError:
        raise EntityAlreadyExistsError("Octane with this grade already exists.")
    return Octane.model_validate(db_octane)


async def delete_octane(id: int, session: AsyncSession) -> Octane:
    db_octane = await find_octane(id, session)
    await session.delete(db_octane)
    await session.commit()
    return Octane.model_dump(db_octane)
