from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import RegisterUserRequest, Token
from core.limiter import limiter
from database.session import get_db_session

from . import services

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/")
@limiter.limit("10/hour")
async def register_user(
    request: Request,
    register_user_request: RegisterUserRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    logger.info(f"Registering user: {register_user_request.username}.")
    result = await services.register_user(register_user_request, db)
    logger.info(f"Registered user: {result}.")
    return result


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_session),
) -> Token:
    logger.info(f"Login attempt for user: {form_data.username}.")
    result = await services.login_for_access_token(form_data, db)
    logger.info(f"Login successful for user: {form_data.username}.")
    return result
