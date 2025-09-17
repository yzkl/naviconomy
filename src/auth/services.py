from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser, RegisterUserRequest
from auth.utils import get_password_hash
from exceptions.exceptions import RegistrationFailed


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
