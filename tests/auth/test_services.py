import pytest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser, RegisterUserRequest, Token, User
from auth.services import (
    authenticate_user,
    get_user_by_username,
    login_for_access_token,
    register_user,
)
from auth.utils import get_password_hash
from exceptions.exceptions import AuthenticationFailed, RegistrationFailed


async def setup(testing_data: dict, async_session: AsyncSession) -> None:
    test_user = DBUser(
        username=testing_data["username"],
        email=testing_data["email"],
        hashed_password=get_password_hash(SecretStr(testing_data["password"])),
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


@pytest.mark.asyncio
async def test_get_user_by_username_returns_None_for_nonexistent_user(
    testing_session,
) -> None:
    user = await get_user_by_username("not a user", testing_session)

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_username_regular(testing_data, testing_session) -> None:
    await setup(testing_data, testing_session)

    user = await get_user_by_username(testing_data["username"], testing_session)

    assert isinstance(user, DBUser)
    assert user.username == testing_data["username"]


@pytest.mark.asyncio
async def test_authenticate_user_returns_None_for_nonexistent_user(
    testing_session,
) -> None:
    authenticated = await authenticate_user("not a user", "weakpass", testing_session)
    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_returns_None_for_incorrect_password(
    testing_data, testing_session
) -> None:
    await setup(testing_data, testing_session)
    authenticated = await authenticate_user(
        testing_data["username"], SecretStr("wrongpass"), testing_session
    )
    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_regular(testing_data, testing_session) -> None:
    await setup(testing_data, testing_session)
    authenticated = await authenticate_user(
        testing_data["username"], SecretStr(testing_data["password"]), testing_session
    )

    assert isinstance(authenticated, User)
    assert authenticated.username == testing_data["username"]


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_nonexistent_user(
    testing_session,
) -> None:
    invalid_user_data = OAuth2PasswordRequestForm(
        username="not-a-user", password="weakpass"
    )

    with pytest.raises(AuthenticationFailed):
        await login_for_access_token(invalid_user_data, testing_session)


@pytest.mark.asyncio
async def test_login_for_access_token_raises_AuthenticationFailed_for_incorrect_password(
    testing_data,
    testing_session,
) -> None:
    await setup(testing_data, testing_session)

    incorrect_password_data = OAuth2PasswordRequestForm(
        username=testing_data["username"], password="wrongpass"
    )

    with pytest.raises(AuthenticationFailed):
        await login_for_access_token(incorrect_password_data, testing_session)


@pytest.mark.asyncio
async def test_login_for_access_token_regular(
    testing_data,
    testing_session,
) -> None:
    await setup(testing_data, testing_session)

    form_data = OAuth2PasswordRequestForm(
        username=testing_data["username"],
        password=testing_data["password"],
    )

    token = await login_for_access_token(form_data, testing_session)

    assert isinstance(token, Token)
    assert token.token_type == "bearer"
