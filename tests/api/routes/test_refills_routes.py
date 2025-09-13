import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models

URL_PREFIX = "/v1/refills/"


async def setup_dimension_tables(async_session: AsyncSession) -> None:
    test_brand_1 = models.Brand(id=1, name="x")
    test_brand_2 = models.Brand(id=2, name="y")
    test_octane_1 = models.Octane(id=1, grade=91)
    test_octane_2 = models.Octane(id=2, grade=95)
    async_session.add_all([test_brand_1, test_brand_2, test_octane_1, test_octane_2])
    await async_session.commit()


async def setup(async_session: AsyncSession) -> None:
    await setup_dimension_tables(async_session)

    test_refill_1 = models.Refill(
        id=1,
        odometer=123.5,
        liters_filled=3.5,
        brand_id=1,
        octane_id=1,
        ethanol_percent=0.1,
        cost=175.5,
    )
    test_refill_2 = models.Refill(
        id=2,
        odometer=456.5,
        liters_filled=3.2,
        brand_id=2,
        octane_id=2,
        ethanol_percent=0.0,
        cost=200.5,
    )
    async_session.add_all([test_refill_1, test_refill_2])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_fill_date(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"fill_date": False})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_odometer(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"odometer": True})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_liters_filled(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        URL_PREFIX, json={"odometer": 123.5, "liters_filled": "full tank"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_brand_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        URL_PREFIX, json={"odometer": 123.5, "liters_filled": 3.5, "brand_id": False}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_octane_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        URL_PREFIX,
        json={
            "odometer": 123.5,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": "some id",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_ethanol_percent(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        URL_PREFIX,
        json={
            "odometer": 123.5,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 2,
            "ethanol_percent": "10%",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_returns_http_422_for_improper_cost(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        URL_PREFIX,
        json={
            "odometer": 123.5,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 2,
            "ethanol_percent": 0.1,
            "cost": "not much",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_refill_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup_dimension_tables(testing_session)
    response = await async_client.post(
        URL_PREFIX,
        json={
            "odometer": 123.5,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 2,
            "ethanol_percent": 0.1,
            "cost": 200.5,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_refill_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "not id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_refill_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX + "1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_refills(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "false")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_fill_date(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={"fill_date": "yesterday"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_odometer(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "1", json={"odometer": "1000 km"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_liters_filled(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        URL_PREFIX + "1", json={"odometer": 1000, "liters_filled": "a gallon"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_brand_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        URL_PREFIX + "1",
        json={"odometer": 1000, "liters_filled": 3.5, "brand_id": "true"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_octane_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        URL_PREFIX + "1",
        json={"odometer": 1000, "liters_filled": 3.5, "brand_id": 1, "octane_id": "1"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_ethanol_percent(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        URL_PREFIX + "1",
        json={
            "odometer": 1000,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 1,
            "ethanol_percent": "5%",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_returns_http_422_for_improper_cost(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        URL_PREFIX + "1",
        json={
            "odometer": 1000,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 1,
            "ethanol_percent": 0.5,
            "cost": "a dime",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_refill_regular(
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup(testing_session)
    response = await async_client.put(
        URL_PREFIX + "1",
        json={
            "odometer": 1000,
            "liters_filled": 3.5,
            "brand_id": 1,
            "octane_id": 1,
            "ethanol_percent": 0.5,
            "cost": 150,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_refill_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "not an id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_refill_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.delete(URL_PREFIX + "2")
    assert response.status_code == 200
