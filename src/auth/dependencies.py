from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.services import get_user_by_username
from auth.utils import verify_token
from database.session import get_db_session
from exceptions.exceptions import InvalidAccountError, InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Fetch the user currently authenticated via an access token.

    Returns a `User` Pydantic model containing the user's information.

    Parameters
    ----------
    token : str
        The token to verify and decode. Injected via `OAuth2PasswordBearer` scheme.

    db : AsyncSession
        The asynchronous session used to query the user. Injected via `get_db_session`.

    Returns
    -------
    User
        A Pydantic model representing the authenticated user.

    Raises
    ------
    InvalidTokenError
        If the token is invalid or expired, or if the username does not exist.
    """
    token_data = verify_token(token)
    db_user = await get_user_by_username(token_data.username, db)
    if not db_user:
        raise InvalidTokenError("Invalid credentials.")
    return User.model_validate(db_user)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Return the authenticated user as a Pydantic model if their account is active.

    Parameters
    ----------
    current_user : User
        The user currently authenticated via an access token. Injected via `get_current_user`.

    Returns
    -------
    User
        A Pydantic model representing the authenticated user.

    Raises
    ------
    InvalidAccountError
        If the user's account has been disabled or deactivated.
    """
    if not current_user.is_active:
        raise InvalidAccountError("Account has been disabled or deactivated.")
    return current_user
