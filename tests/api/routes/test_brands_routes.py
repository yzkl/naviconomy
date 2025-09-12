import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import models
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError

URL_PREFIX = "/brand/"


async def setup(async_session: AsyncSession) -> None:
    test_brand = models.Brand(id=1, name="test brand")
    other_brand = models.Brand(id=2, name="other brand")
    async_session.add_all([test_brand, other_brand])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_brand_returns_http_422_for_missing_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_brand_returns_http_422_for_invalid_name_type(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": False})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_brand_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    # Seed test brands
    await setup(testing_session)
    # Create an existing brand
    with pytest.raises(EntityAlreadyExistsError):
        await async_client.post(URL_PREFIX, json={"name": "test brand"})


@pytest.mark.asyncio
async def test_create_brand_regular(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(URL_PREFIX, json={"name": "brand x"})

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "brand x"


@pytest.mark.asyncio
async def test_read_brand_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX + "true")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_brand_raises_EntityDoesNotExistError(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.get(URL_PREFIX + "1")


@pytest.mark.asyncio
async def test_read_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.get(URL_PREFIX + "1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "test brand"


@pytest.mark.asyncio
async def test_read_brands_returns_empty_list(async_client: AsyncClient) -> None:
    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_brands_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "test brand"
    assert response.json()[1]["name"] == "other brand"


@pytest.mark.asyncio
async def test_update_brand_returns_http_422_for_invalid_id_value(
    testing_session: AsyncSession,
    async_client: AsyncClient,
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.put(URL_PREFIX + "false", json={"name": "some"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_brand_returns_http_422_for_invalid_parameters(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.put(URL_PREFIX + "2", json={"name": 123})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_brand_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    # Update one brand to match the other
    with pytest.raises(EntityAlreadyExistsError):
        await async_client.put(URL_PREFIX + "1", json={"name": "other brand"})


@pytest.mark.asyncio
async def test_update_brand_raises_EntityDoesNotExistError(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.put(URL_PREFIX + "503", json={"name": "other brand"})


@pytest.mark.asyncio
async def test_update_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    result = await async_client.put(URL_PREFIX + "2", json={"name": "brand x"})

    assert result.status_code == 200
    assert result.json()["id"] == 2
    assert result.json()["name"] == "brand x"


@pytest.mark.asyncio
async def test_delete_brand_returns_http_422(async_client: AsyncClient) -> None:
    response = await async_client.delete(URL_PREFIX + "true")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_brand_raises_EntityDoesNotExistError(
    async_client: AsyncClient,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await async_client.delete(URL_PREFIX + "404")


@pytest.mark.asyncio
async def test_delete_brand_regular(
    testing_session: AsyncSession, async_client: AsyncClient
) -> None:
    # Seed test brands
    await setup(testing_session)

    response = await async_client.delete(URL_PREFIX + "1")
    table_contents = await async_client.get(URL_PREFIX)

    assert response.status_code == 200
    assert response.json()["name"] == "test brand"
    assert table_contents.status_code == 200
    assert isinstance(table_contents.json(), list)
    assert len(table_contents.json()) == 1
    assert table_contents.json()[0]["name"] == "other brand"
