from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth.models import DBUser
from auth.utils import create_access_token, get_password_hash
from database.session import get_db_session
from main import app

URL_PREFIX = "/api/v1/"


async def setup_dimensions(testing_data: dict, async_session: AsyncSession) -> None:
    test_brand_1 = models.Brand(id=1, name=testing_data["brand1"])
    test_brand_2 = models.Brand(id=2, name=testing_data["brand2"])
    test_octane_1 = models.Octane(id=1, grade=testing_data["octane1"])
    test_octane_2 = models.Octane(id=2, grade=testing_data["octane2"])
    async_session.add_all([test_brand_1, test_brand_2, test_octane_1, test_octane_2])
    await async_session.commit()


async def setup_facts(testing_data: dict, async_session: AsyncSession) -> None:
    await setup_dimensions(testing_data, async_session)

    test_refill_1 = models.Refill(**testing_data["refill1"])
    test_refill_2 = models.Refill(**testing_data["refill2"])

    async_session.add_all([test_refill_1, test_refill_2])
    await async_session.commit()


async def setup_users(testing_data: dict, async_session: AsyncSession) -> None:
    test_user_1 = DBUser(
        username=testing_data["user"]["username"],
        email=testing_data["user"]["email"],
        hashed_password=get_password_hash(SecretStr(testing_data["user"]["password"])),
    )
    test_user_2 = DBUser(
        username=testing_data["deactivated_user"]["username"],
        email=testing_data["deactivated_user"]["email"],
        hashed_password=get_password_hash(
            SecretStr(testing_data["deactivated_user"]["password"])
        ),
        is_active=False,
    )
    async_session.add_all([test_user_1, test_user_2])
    await async_session.commit()


@pytest.mark.asyncio
async def test_read_root_returns_http_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "server is running" in response.text


@pytest.mark.asyncio
async def test_brands_route_is_registered(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "brands/")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_octanes_route_is_registered(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "octanes/")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_refills_route_is_registered(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "refills/")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_register_route_is_registered(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/auth/",
        json={
            "username": "new-user",
            "email": "email@email.com",
            "password": "pass123",
        },
    )
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_login_route_is_registered(async_client: AsyncClient) -> None:
    form_data = {
        "username": "new-user",
        "password": "some-pass",
    }
    response = await async_client.post(
        "/api/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_register_user_returns_http_401_for_duplicate_username(
    testing_data: dict,
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup_users(testing_data, testing_session)
    response = await async_client.post(
        "/api/auth/",
        json={
            "username": testing_data["user"]["username"],
            "email": "email@email.com",
            "password": "pass123",
        },
    )
    assert response.status_code == 401
    assert "Username has already been taken" in response.text


@pytest.mark.asyncio
async def test_register_user_returns_http_401_for_duplicate_email(
    testing_data: dict,
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup_users(testing_data, testing_session)
    response = await async_client.post(
        "/api/auth/",
        json={
            "username": "new-user",
            "email": testing_data["user"]["email"],
            "password": "pass123",
        },
    )
    assert response.status_code == 401
    assert "Email has already been taken" in response.text


@pytest.mark.asyncio
async def test_login_returns_http_401_for_invalid_username(
    async_client: AsyncClient,
) -> None:
    form_data = {
        "username": "not-user",
        "password": "some-pass",
    }
    response = await async_client.post(
        "/api/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.text


@pytest.mark.asyncio
async def test_login_returns_http_401_for_invalid_password(
    testing_data: dict,
    async_client: AsyncClient,
) -> None:
    form_data = {
        "username": testing_data["user"]["username"],
        "password": "some-pass",
    }
    response = await async_client.post(
        "/api/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_401_for_invalid_token(
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        invalid_token = "not-a-token"
        response = await client.get(
            URL_PREFIX + "brands/1",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_401_for_expired_token(
    testing_data: dict,
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        expired_token = create_access_token(
            {"sub": testing_data["user"]}, now_fn=lambda: datetime(2025, 1, 1)
        )
        response = await client.get(
            URL_PREFIX + "brands/1",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_401_for_missing_sub_claim(
    testing_session: AsyncSession,
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        missing_sub = create_access_token({"obj": "no-sub"})
        response = await client.get(
            URL_PREFIX + "brands/1",
            headers={"Authorization": f"Bearer {missing_sub}"},
        )

    assert response.status_code == 401
    assert "Missing a 'sub" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_403_for_deactivated_user(
    testing_data: dict, testing_session: AsyncSession
) -> None:
    async def override_db():
        yield testing_session

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        deactivated_user_token = create_access_token(
            {"sub": testing_data["deactivated_user"]["username"]}
        )
        await setup_users(testing_data, testing_session)

        response = await client.get(
            URL_PREFIX + "brands/1",
            headers={"Authorization": f"Bearer {deactivated_user_token}"},
        )

        assert response.status_code == 403
        assert "Account has been disabled" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_404_for_reading_nonexistent_brand(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "brands/1000")
    assert response.status_code == 404
    assert "Brand" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_404_for_reading_nonexistent_octane(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "octanes/1000")
    assert response.status_code == 404
    assert "Octane" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_404_for_reading_nonexistent_refill(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(URL_PREFIX + "refills/1000")
    assert response.status_code == 404
    assert "Refill" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_409_for_creating_duplicate_brand(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.post(
        URL_PREFIX + "brands/", json={"name": testing_data["brand1"]}
    )
    assert response.status_code == 409
    assert "Brand already exists" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_409_for_updating_duplicate_brand(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.put(
        URL_PREFIX + "brands/2", json={"name": testing_data["brand1"]}
    )
    assert response.status_code == 409
    assert "Brand" in response.text
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_409_for_creating_duplicate_octane(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.post(
        URL_PREFIX + "octanes/", json={"grade": testing_data["octane1"]}
    )
    assert response.status_code == 409
    assert "Octane already exists" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_409_for_updating_duplicate_octane(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.put(
        URL_PREFIX + "octanes/2", json={"grade": testing_data["octane1"]}
    )
    assert response.status_code == 409
    assert "Octane" in response.text
    assert "already exists" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_422_for_creating_refill_with_nonexistent_brand(
    testing_data: dict, async_client: AsyncClient
) -> None:
    payload = testing_data["refill1"].copy()
    payload.pop("id")
    response = await async_client.post(URL_PREFIX + "refills/", json=payload)
    assert response.status_code == 422
    assert "Brand" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_422_for_creating_refill_with_nonexistent_octane(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    payload = testing_data["refill1"].copy()
    payload.pop("id")
    payload["octane_id"] = 1000
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.post(URL_PREFIX + "refills/", json=payload)
    assert response.status_code == 422
    assert "Octane" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_422_for_updating_refill_with_nonexistent_brand(
    testing_data: dict,
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup_facts(testing_data, testing_session)
    response = await async_client.put(URL_PREFIX + "refills/1", json={"brand_id": 1000})
    assert response.status_code == 422
    assert "Brand" in response.text
    assert "does not exist" in response.text


@pytest.mark.asyncio
async def test_main_returns_http_422_for_updating_refill_with_nonexistent_octane(
    testing_data: dict,
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup_facts(testing_data, testing_session)
    response = await async_client.put(
        URL_PREFIX + "refills/1", json={"octane_id": 1000}
    )
    assert response.status_code == 422
    assert "Octane" in response.text
    assert "does not exist" in response.text
