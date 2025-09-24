import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas import RefillCreate

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

    test_refill_1 = models.Refill(RefillCreate(testing_data["refill1"]))
    test_refill_2 = models.Refill(RefillCreate(testing_data["refill2"]))

    async_session.add_all([test_refill_1, test_refill_2])
    await async_session.commit()


@pytest.mark.asyncio
async def test_read_root_returns_http_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "server is running" in response.text


@pytest.mark.asyncio
async def test_create_brand_returns_http_200(
    testing_data: dict, async_client: AsyncClient
) -> None:
    response = await async_client.post(
        URL_PREFIX + "brands/", json={"name": testing_data["brand1"]}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_brand_returns_http_200(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.get(URL_PREFIX + "brands/1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_brands_returns_http_200(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.get(URL_PREFIX + "brands/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_brand_returns_http_200(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.put(
        URL_PREFIX + "brands/1", json={"name": "new-brand"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_brand_returns_http_200(
    testing_data: dict, testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimensions(testing_data, testing_session)
    response = await async_client.delete(URL_PREFIX + "brands/1")
    assert response.status_code == 200
