import pytest
from httpx import AsyncClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import DBUser
from auth.utils import get_password_hash

URL_PREFIX = "/auth/"


async def setup(testing_data: dict, testing_session: AsyncSession) -> None:
    test_user = DBUser(
        username=testing_data["username"],
        email=testing_data["email"],
        hashed_password=get_password_hash(SecretStr(testing_data["password"])),
    )
    testing_session.add(test_user)
    await testing_session.commit()


@pytest.mark.asyncio
async def test_register_user_returns_regular(
    testing_data, async_client: AsyncClient
) -> None:
    response = await async_client.post(
        URL_PREFIX, json=testing_data["register_payload"]
    )

    assert response.status_code == 200
    assert (
        f"Welcome to Naviconomy, {testing_data['register_payload']['username']}"
    ) in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_for_access_token_regular(
    testing_data, testing_session, async_client: AsyncClient
) -> None:
    await setup(testing_data, testing_session)

    form_data = {
        "username": testing_data["username"],
        "password": testing_data["password"],
    }

    response = await async_client.post(
        URL_PREFIX + "token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
