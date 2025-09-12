from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import brands
from database.session import get_db_session
from schemas import Brand, BrandCreate, BrandUpdate

router = APIRouter(prefix="/brand")


@router.post("/", response_model=Brand)
@limiter.limit("60/minute")
async def create_brand(
    request: Request, params: BrandCreate, db: AsyncSession = Depends(get_db_session)
) -> Brand:
    logger.info(f"Creating brand: {params}.")
    result = await brands.create_brand(params, db)
    logger.info(f"Created brand: {result}.")
    return result


@router.get("/{id}", response_model=Brand)
@limiter.limit("60/minute")
async def read_brand(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Brand:
    logger.info(f"Fetching brand with id: {id}.")
    result = await brands.read_brand(id, db)
    logger.info(f"Fetched brand: {result}.")
    return result


@router.get("/", response_model=List[Brand])
@limiter.limit("60/minute")
async def read_brands(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Brand]:
    logger.info("Fetching all brands.")
    result = await brands.read_brands(db)
    logger.info("Fetched all brands.")
    return result


@router.put("/{id}", response_model=Brand)
@limiter.limit("60/minute")
async def update_brand(
    request: Request,
    id: int,
    params: BrandUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Brand:
    logger.info(f"Updating brand with id: {id}.")
    result = await brands.update_brand(id, params, db)
    logger.info(f"Updated brand: {result}.")
    return result


@router.delete("/{id}", response_model=Brand)
@limiter.limit("60/minute")
async def delete_brand(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Brand:
    logger.info(f"Deleting brand with id: {id}.")
    result = await brands.delete_brand(id, db)
    logger.info(f"Deleted brand: {result}.")
    return result
