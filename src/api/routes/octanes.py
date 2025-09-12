from typing import List

from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.limiter import limiter
from crud import octanes
from database.session import get_db_session
from schemas import Octane, OctaneCreate, OctaneUpdate

router = APIRouter(prefix="/octane")


@router.post("/", response_model=Octane)
@limiter.limit("60/minute")
async def create_octane(
    request: Request, params: OctaneCreate, db: AsyncSession = Depends(get_db_session)
) -> Octane:
    logger.info(f"Creating octane: {params}.")
    result = await octanes.create_octane(params, db)
    logger.info(f"Created octane: {result}.")
    return result


@router.get("/{id}", response_model=Octane)
@limiter.limit("60/minute")
async def read_octane(
    request: Request, id: int, db: AsyncSession = Depends(get_db_session)
) -> Octane:
    logger.info(f"Fetching octane with id: {id}.")
    result = await octanes.read_octane(id, db)
    logger.info(f"Fetched octane: {result}.")
    return result


@router.get("/", response_model=List[Octane])
@limiter.limit("60/minute")
async def read_octanes(
    request: Request, db: AsyncSession = Depends(get_db_session)
) -> List[Octane]:
    logger.info("Fetching octanes.")
    result = await octanes.read_octanes(db)
    logger.info("Fetched octanes.")
    return result


@router.put("/{id}", response_model=Octane)
@limiter.limit("60/minute")
async def update_octane(
    request: Request,
    id: int,
    params: OctaneUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Octane:
    logger.info(f"Updating octane with id: {id}.")
    result = await octanes.update_octane(id, params, db)
    logger.info(f"Updated octane: {result}.")
    return result
