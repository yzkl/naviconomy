from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Brand, BrandCreate, BrandUpdate


async def create_brand(params: BrandCreate, session: AsyncSession) -> Brand:
    db_brand = models.Brand(**params.model_dump())
    session.add(db_brand)
    try:
        await session.commit()
        await session.refresh(db_brand)
    except IntegrityError:
        raise EntityAlreadyExistsError("Brand already exists.")
    return Brand.model_validate(db_brand)


async def find_brand(id: int, session: AsyncSession) -> models.Brand:
    db_brand = await session.get(models.Brand, id)
    if not db_brand:
        raise EntityDoesNotExistError(f"Brand with id {id} does not exist.")
    return db_brand


async def find_brands(session: AsyncSession) -> List[models.Brand]:
    stmt = select(models.Brand).order_by(models.Brand.id)
    db_brands = (await session.scalars(stmt)).all()
    return db_brands


async def read_brand(id: int, session: AsyncSession) -> Brand:
    db_brand = await find_brand(id, session)
    return Brand.model_validate(db_brand)


async def read_brands(session: AsyncSession) -> List[Brand]:
    db_brands = await find_brands(session)
    return [Brand.model_validate(db_brand) for db_brand in db_brands]


async def update_brand(id: int, params: BrandUpdate, session: AsyncSession) -> Brand:
    db_brand = await find_brand(id, session)
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(db_brand, attr, value)
    session.add(db_brand)
    try:
        await session.commit()
        await session.refresh(db_brand)
    except IntegrityError:
        raise EntityAlreadyExistsError("Brand with this name already exists.")
    return Brand.model_validate(db_brand)


async def delete_brand(id: int, session: AsyncSession) -> Brand:
    db_brand = await find_brand(id, session)
    await session.delete(db_brand)
    await session.commit()
    return Brand.model_validate(db_brand)
