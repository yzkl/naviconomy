import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser, RegisterUserRequest
from auth.services import register_user
from auth.utils import get_password_hash
from exceptions.exceptions import RegistrationFailed


async def setup(testing_data: dict, async_session: AsyncSession) -> None:
    test_user = DBUser(
        username=testing_data["username"],
        email=testing_data["email"],
        hashed_password=get_password_hash(testing_data["password"]),
    )
    async_session.add(test_user)
    await async_session.commit()


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_username(
    testing_data: dict, testing_session: AsyncSession
) -> None:
    await setup(testing_data, testing_session)
    payload = testing_data["register_payload"].copy()
    payload.update({"email": "new@email.com"})

    with pytest.raises(RegistrationFailed, match="Username has already been taken"):
        await register_user(
            RegisterUserRequest(**payload),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_email(
    testing_data, testing_session
) -> None:
    await setup(testing_data, testing_session)
    payload = testing_data["register_payload"].copy()
    payload.update({"username": "new-user"})

    with pytest.raises(RegistrationFailed, match="Email has already been taken"):
        await register_user(
            RegisterUserRequest(**payload),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_raises_RegistrationFailed_for_duplicate_username_and_email(
    testing_data, testing_session
) -> None:
    await setup(testing_data, testing_session)

    with pytest.raises(RegistrationFailed, match="Username has already been taken"):
        await register_user(
            RegisterUserRequest(**testing_data["register_payload"]),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_pseudo_username_race_condition(
    testing_data, testing_session
) -> None:
    await register_user(
        RegisterUserRequest(
            username=testing_data["username"],
            email=testing_data["email"],
            password="pass123",
        ),
        testing_session,
    )

    # Second registration should fail
    with pytest.raises(RegistrationFailed):
        await register_user(
            RegisterUserRequest(
                username=testing_data["username"],
                email="new@email.com",
                password="pass123",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_pseudo_email_race_condition(
    testing_data, testing_session
) -> None:
    await register_user(
        RegisterUserRequest(
            username=testing_data["username"],
            email=testing_data["email"],
            password="pass123",
        ),
        testing_session,
    )

    # Second registration should fail
    with pytest.raises(RegistrationFailed):
        await register_user(
            RegisterUserRequest(
                username="new-user",
                email=testing_data["email"],
                password="pass123",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_register_user_regular(testing_data, testing_session) -> None:
    result = await register_user(
        RegisterUserRequest(**testing_data["register_payload"]), testing_session
    )

    assert isinstance(result, dict)
    assert testing_data["username"] in result["detail"]
