from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import refills
from database.session import get_db_session
from schemas import Refill, RefillCreate, RefillUpdate

router = APIRouter(prefix="/refill")


@router.post("/", response_model=Refill)
@limiter.limit("60/minute")
async def create_refill(
    request: Request, params: RefillCreate, db: AsyncSession = Depends(get_db_session)
) -> Refill:
    logger.info(f"Creating refill: {params}.")
    result = await refills.create_refill(params, db)
    logger.info(f"Created refill: {result}.")
    return result


@router.get("/{id}", response_model=Refill)
@limiter.limit("60/minute")
async def read_refill(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Refill:
    logger.info(f"Fetching refill with id: {id}.")
    result = await refills.read_refill(id, db)
    logger.info(f"Fethced refill: {result}.")
    return result


@router.get("/", response_model=List[Refill])
@limiter.limit("60/minute")
async def read_refills(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Refill]:
    logger.info("Fetching refills.")
    result = await refills.read_refills(db)
    logger.info("Fetched refills.")
    return result


@router.put("/{id}", response_model=Refill)
@limiter.limit("60/minute")
async def update_refill(
    request: Request,
    id: int,
    params: RefillUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Refill:
    logger.info(f"Updating refill with id: {id}.")
    result = await refills.update_refill(id, params, db)
    logger.info(f"Updated refill: {result}.")
    return result
