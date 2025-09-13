import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models

URL_PREFIX = "/v1/octanes/"


async def setup(async_session: AsyncSession) -> None:
    test_octane = models.Octane(id=1, grade=91)
    other_octane = models.Octane(id=2, grade=95)
    async_session.add_all([test_octane, other_octane])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_octane_returns_http_422_for_improper_parameter(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"grade": "123"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_octane_regular(async_client: AsyncClient) -> None:
    response = await async_client.post(URL_PREFIX, json={"grade": 97})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_octane_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "true")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_octane_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX + "1")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_read_octanes(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.get(URL_PREFIX)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_octane_returns_http_422_for_improper_id(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(URL_PREFIX + "false")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_octane_returns_http_422_for_improper_parameter(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.put(URL_PREFIX + "1", json={"grade": "97"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_octane_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.put(URL_PREFIX + "1", json={"grade": 97})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_octane_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "false")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    await setup(testing_session)
    response = await async_client.delete(URL_PREFIX + "2")
    assert response.status_code == 200
