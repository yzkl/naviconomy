from datetime import datetime

import pytest
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user, get_current_user
from auth.models import DBUser, User
from auth.utils import create_access_token, get_password_hash
from exceptions.exceptions import InvalidAccountError, InvalidTokenError


async def setup(testing_data: dict, async_session: AsyncSession) -> None:
    test_user = DBUser(
        username=testing_data["username"],
        email=testing_data["email"],
        hashed_password=get_password_hash(SecretStr(testing_data["password"])),
    )
    async_session.add(test_user)
    await async_session.commit()


@pytest.mark.asyncio
async def test_get_current_user_raises_InvalidTokenError_for_invalid_jwt(
    testing_session,
) -> None:
    invalid_token = "not-a-token"

    with pytest.raises(InvalidTokenError):
        await get_current_user(invalid_token, testing_session)


@pytest.mark.asyncio
async def test_get_current_user_raises_InvalidTokenError_for_expired_jwt(
    testing_data, testing_session
) -> None:
    expired = create_access_token(
        data={"sub": testing_data["username"]}, now_fn=lambda: datetime(2025, 1, 1)
    )

    with pytest.raises(InvalidTokenError):
        await get_current_user(expired, testing_session)


@pytest.mark.asyncio
async def test_get_current_user_regular(testing_data, testing_session) -> None:
    await setup(testing_data, testing_session)

    token = create_access_token({"sub": testing_data["username"]})

    user = await get_current_user(token, testing_session)

    assert isinstance(user, User)
    assert user.username == testing_data["username"]
    assert user.email == testing_data["email"]
    assert user.is_active


@pytest.mark.asyncio
async def test_get_current_active_user_raises_InvalidAccountError() -> None:
    # Create a deactivated user
    inactive_user = User(
        username="inactive-user", email="some@email.com", is_active=False
    )

    with pytest.raises(InvalidAccountError):
        await get_current_active_user(current_user=inactive_user)


@pytest.mark.asyncio
async def test_get_current_active_user_regular(testing_data) -> None:
    test_user = User(
        username=testing_data["username"], email=testing_data["email"], is_active=True
    )

    active_user = await get_current_active_user(current_user=test_user)

    assert isinstance(active_user, User)
    assert active_user.username == testing_data["username"]
    assert active_user.email == testing_data["email"]
    assert active_user.is_active
