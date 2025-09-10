import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import octanes
from exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from schemas import Octane, OctaneCreate, OctaneUpdate


async def setup(async_session: AsyncSession) -> None:
    test_octane = models.Octane(id=1, grade=91)
    other_octane = models.Octane(id=2, grade=95)
    async_session.add_all([test_octane, other_octane])
    await async_session.commit()


@pytest.mark.asyncio
async def test_create_octane_raises_ValidationErorr(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await octanes.create_octane(OctaneCreate(grade=False), testing_session)
    with pytest.raises(ValidationError):
        await octanes.create_octane(OctaneCreate(grade="True"), testing_session)


@pytest.mark.asyncio
async def test_create_octane_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    # Create an existing octane
    with pytest.raises(EntityAlreadyExistsError):
        await octanes.create_octane(OctaneCreate(grade=91), testing_session)


@pytest.mark.asyncio
async def test_create_octane_regular(
    testing_session: AsyncSession,
) -> None:
    result = await octanes.create_octane(OctaneCreate(grade=97), testing_session)

    assert isinstance(result, Octane)
    assert result.id == 1
    assert result.grade == 97


@pytest.mark.asyncio
async def test_find_octane_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await octanes.find_octane(404, testing_session)


@pytest.mark.asyncio
async def test_find_octane_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.find_octane(1, testing_session)

    assert isinstance(result, models.Octane)
    assert result.id == 1
    assert result.grade == 91


@pytest.mark.asyncio
async def test_find_octanes_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    result = await octanes.find_octanes(testing_session)

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_find_octanes_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.find_octanes(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Octane)
    assert result[0].id == 1
    assert result[0].grade == 91
    assert isinstance(result[1], models.Octane)
    assert result[1].id == 2
    assert result[1].grade == 95


@pytest.mark.asyncio
async def test_read_octane_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await octanes.read_octane(404, testing_session)


@pytest.mark.asyncio
async def test_read_octane_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.read_octane(2, testing_session)

    assert isinstance(result, Octane)
    assert result.id == 2
    assert result.grade == 95


@pytest.mark.asyncio
async def test_read_octanes_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    result = await octanes.read_octanes(testing_session)

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_read_octanes_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.read_octanes(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Octane)
    assert result[0].id == 1
    assert result[0].grade == 91
    assert isinstance(result[1], Octane)
    assert result[1].id == 2
    assert result[1].grade == 95


@pytest.mark.asyncio
async def test_update_octane_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await octanes.update_octane(404, OctaneUpdate(grade=97), testing_session)


@pytest.mark.asyncio
async def test_update_octane_raises_EntityAlreadyExistsError(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    # Change the grade of one to match the other
    with pytest.raises(EntityAlreadyExistsError):
        await octanes.update_octane(1, OctaneUpdate(grade=95), testing_session)


@pytest.mark.asyncio
async def test_update_octane_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.update_octane(2, OctaneUpdate(grade=97), testing_session)

    assert isinstance(result, Octane)
    assert result.id == 2
    assert result.grade == 97


@pytest.mark.asyncio
async def test_delete_octane_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await octanes.delete_octane(404, testing_session)


@pytest.mark.asyncio
async def test_delete_octane_regular(
    testing_session: AsyncSession,
) -> None:
    # Add test octanes
    await setup(testing_session)

    result = await octanes.delete_octane(1, testing_session)
    table_contents = await octanes.read_octanes(testing_session)

    assert isinstance(result, Octane)
    assert result.id == 1
    assert result.grade == 91
    assert isinstance(table_contents, list)
    assert len(table_contents) == 1
    assert isinstance(table_contents[0], Octane)
    assert table_contents[0].id == 2
    assert table_contents[0].grade == 95
