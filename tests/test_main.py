import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models

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
