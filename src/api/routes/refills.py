from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import refills
from database.session import get_db_session
from schemas import Refill, RefillCreate

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
