import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_base_router_brands_route_is_registered(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/v1/brands/")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_base_router_octanes_route_is_registered(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/v1/octanes/")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_base_router_refills_route_is_registered(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/v1/refills/")
    assert response.status_code != 404
