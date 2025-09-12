import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models

URL_PREFIX = "/brand/"


async def setup(async_session: AsyncSession) -> None:
    test_brand = models.Brand(id=1, name="test brand")
    other_brand = models.Brand(id=2, name="other brand")
    async_session.add_all([test_brand, other_brand])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_brand_returns_http_422_for_improper_parameter(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": False})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_brand_regular(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": "brand x"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_brand_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "true")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX + "1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_brandsr(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_brand_returns_http_422_for_improper_id(
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    await setup(testing_session)
    response = await async_client.put(URL_PREFIX + "false", json={"name": "some"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_brand_returns_http_422_for_improper_parameters(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.put(URL_PREFIX + "2", json={"name": 123})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    result = await async_client.put(URL_PREFIX + "2", json={"name": "brand x"})
    assert result.status_code == 200


@pytest.mark.asyncio
async def test_delete_brand_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "true")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.delete(URL_PREFIX + "1")
    assert response.status_code == 200
