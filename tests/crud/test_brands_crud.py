import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import brands
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Brand, BrandCreate, BrandUpdate


async def setup(async_session: AsyncSession) -> None:
    test_brand = models.Brand(id=1, name="test brand")
    other_brand = models.Brand(id=2, name="other brand")
    async_session.add_all([test_brand, other_brand])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_brand_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await brands.create_brand(BrandCreate(name=False), testing_session)
    with pytest.raises(ValidationError):
        await brands.create_brand(BrandCreate(name=1), testing_session)


@pytest.mark.asyncio
async def test_create_brand_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Create test brands
    await setup(testing_session)

    # Create a similar test brand
    with pytest.raises(EntityAlreadyExistsError):
        await brands.create_brand(BrandCreate(name="test brand"), testing_session)


@pytest.mark.asyncio
async def test_create_brand_regular(testing_session: AsyncSession) -> None:
    result = await brands.create_brand(BrandCreate(name="Test Brand"), testing_session)

    assert isinstance(result, Brand)
    assert result.id == 1
    assert result.name == "Test Brand"


@pytest.mark.asyncio
async def test_find_brand_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await brands.find_brand(101, testing_session)


@pytest.mark.asyncio
async def test_find_brand_regular(
    testing_session: AsyncSession,
) -> None:
    # Create test brands
    await setup(testing_session)

    result = await brands.find_brand(1, testing_session)

    assert isinstance(result, models.Brand)
    assert result.name == "test brand"


@pytest.mark.asyncio
async def test_find_brands_return_empty_list(
    testing_session: AsyncSession,
) -> None:
    # Retrieve table contents
    result = await brands.find_brands(testing_session)

    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []


@pytest.mark.asyncio
async def test_find_brands_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    # Retrieve table contents
    result = await brands.find_brands(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Brand)
    assert result[0].id == 1
    assert result[0].name == "test brand"
    assert isinstance(result[1], models.Brand)
    assert result[1].id == 2
    assert result[1].name == "other brand"


@pytest.mark.asyncio
async def test_read_brand_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await brands.read_brand(5000, testing_session)


@pytest.mark.asyncio
async def test_read_brand_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    result = await brands.read_brand(1, testing_session)

    assert isinstance(result, Brand)
    assert result.name == "test brand"


@pytest.mark.asyncio
async def test_read_brands_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    result = await brands.read_brands(testing_session)

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_read_brands_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    # Retrieve table contents
    result = await brands.read_brands(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Brand)
    assert result[0].id == 1
    assert result[0].name == "test brand"
    assert isinstance(result[1], Brand)
    assert result[1].id == 2
    assert result[1].name == "other brand"


@pytest.mark.asyncio
async def test_update_brand_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await brands.update_brand(5000, BrandUpdate(name="some name"), testing_session)


@pytest.mark.asyncio
async def test_update_brand_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    # Update one brand to match the name of the other brand
    with pytest.raises(EntityAlreadyExistsError):
        await brands.update_brand(1, BrandUpdate(name="other brand"), testing_session)


@pytest.mark.asyncio
async def test_update_brand_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    result = await brands.update_brand(
        2, BrandUpdate(name="new brand"), testing_session
    )

    assert isinstance(result, Brand)
    assert result.name == "new brand"


@pytest.mark.asyncio
async def test_delete_brand_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await brands.delete_brand(5000, testing_session)


@pytest.mark.asyncio
async def test_delete_brand_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test brands
    await setup(testing_session)

    result = await brands.delete_brand(1, testing_session)
    table_contents = await brands.read_brands(testing_session)

    # Check that the test brand was deleted
    assert isinstance(result, Brand)
    assert result.name == "test brand"

    # Check the table's contents
    assert isinstance(table_contents, list)
    assert len(table_contents) == 1
    assert isinstance(table_contents[0], Brand)
    assert table_contents[0].name == "other brand"
