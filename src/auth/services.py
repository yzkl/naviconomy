from datetime import timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser, RegisterUserRequest, Token, User
from auth.utils import create_access_token, get_password_hash, verify_password
from config.settings import settings
from exceptions.exceptions import AuthenticationFailed, RegistrationFailed

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


async def register_user(
    register_user_request: RegisterUserRequest, session: AsyncSession
) -> dict:
    """Register a new user in the database.

    Returns a dictionary containing a message for the newly registered user.

    Parameters
    ----------
    register_user_request : RegisterUserRequest
        A pydantic model containing user's registration details (username, email, password).

    session : AsyncSession
        The asynchronous session used to persist the user.

    Returns
    -------
    dict
        A dictionary with a message addressed for the newly registered user.

    Raises
    ------
    RegistrationFailed
        When the username or email is already in use, or a commit conflict occurs.
    """
    # First, check if the username or password input already exists
    existing_user = (
        await session.execute(
            select(DBUser).where(
                or_(
                    DBUser.username == register_user_request.username,
                    DBUser.email == register_user_request.email,
                )
            )
        )
    ).scalar_one_or_none()

    if existing_user:
        if existing_user.username == register_user_request.username:
            raise RegistrationFailed("Username has already been taken.")
        if existing_user.email == register_user_request.email:
            raise RegistrationFailed("Email has already been taken.")

    # Register the new user
    db_user = DBUser(
        id=uuid4(),
        username=register_user_request.username,
        email=register_user_request.email,
        hashed_password=get_password_hash(register_user_request.password),
    )
    session.add(db_user)
    try:
        await session.commit()
        await session.refresh(db_user)
    except IntegrityError:
        raise RegistrationFailed(
            "Conflict detected during registration. Please try a different username or email."
        )
    return {"detail": f"Welcome to Naviconomy, {db_user.username}!"}


async def get_user_by_username(username: str, session: AsyncSession) -> DBUser | None:
    """Fetch a user from the database by their username.

    Returns a `DBUser` SQLAlchemy model containing the user's information if found; otherwise returns `None`.

    Parameters
    ----------
    username : str
        The username of the user to fetch.

    session : AsyncSession
        The asynchronous session used to fetch the user.

    Returns
    -------
    DBUser | None
        A SQLAlchemy model representing the user if found, otherwise `None`.
    """
    db_user = (
        await session.execute(select(DBUser).where(DBUser.username == username))
    ).scalar_one_or_none()
    return db_user


async def authenticate_user(
    username: str, password: SecretStr, session: AsyncSession
) -> User | None:
    """Authenticate a user by their username and password.

    Returns `User` Pydantic model if the authentication is successful; otherwise, returns `None`.

    Parameters
    ----------
    username : str
        The username of the user to authenticate.

    password : SecretStr
        The secret-wrapped password to verify.

    session : AsyncSession
        The asynchronous session used to query the user.

    Returns
    -------
    User | None
        A Pydantic model representing the user if authentication succeeds, otherwise `None`.
    """
    db_user = await get_user_by_username(username, session)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return User.model_validate(db_user)


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession
) -> Token:
    """Authenticate a user using form data and return an access token if credentials are valid.

    Returns a `Token` Pydantic model if the username exists and the password is valid.

    Parameters
    ----------
    form_data : OAuth2PasswordRequestForm
        A FastAPI dependenct that extracts `username` and `password` from a form. Injected via `Depends`.

    session : AsyncSession
        The asynchronous session used to query the user.

    Returns
    -------
    Token
        A Pydantic model containing the access token and its type.

    Raises
    ------
    AuthenticationFailed
        If the username or password is invalid.
    """
    user = await authenticate_user(
        form_data.username, SecretStr(form_data.password), session
    )

    if not user:
        raise AuthenticationFailed("Invalid username or password.")

    access_token = create_access_token(
        {"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(access_token=access_token, token_type="bearer")
