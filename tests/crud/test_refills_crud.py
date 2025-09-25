from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import models
from crud import refills
from exceptions.exceptions import (
    EntityDoesNotExistError,
    RelatedEntityDoesNotExistError,
)
from schemas import Refill, RefillCreate, RefillUpdate


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
        liters_filled=3.50,
        brand_id=1,
        octane_id=1,
        ethanol_percent=0.10,
        cost=175.00,
    )
    test_refill_2 = models.Refill(
        id=2,
        fill_date=date.today() + timedelta(days=1),
        odometer=456.7,
        liters_filled=3.7,
        brand_id=1,
        octane_id=2,
        ethanol_percent=0.0,
        cost=200.5,
    )

    async_session.add_all([test_refill_1, test_refill_2])

    await async_session.commit()


@pytest.mark.asyncio
async def test_create_refill_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(ValidationError):
        await refills.create_refill(RefillCreate(fill_date=True), testing_session)

    with pytest.raises(ValidationError):
        await refills.create_refill(RefillCreate(odometer="123"), testing_session)

    with pytest.raises(ValidationError):
        await refills.create_refill(
            RefillCreate(odometer=123, liters_filled="1.23"), testing_session
        )

    with pytest.raises(ValidationError):
        await refills.create_refill(
            RefillCreate(odometer=123, liters_filled=1.23, brand_id="1"),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.create_refill(
            RefillCreate(odometer=123, liters_filled=1.23, brand_id=1, octane_id="1"),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.create_refill(
            RefillCreate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1,
                ethanol_percent="0.1",
            ),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.create_refill(
            RefillCreate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1,
                ethanol_percent=0.1,
                cost="not much",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_create_refill_raises_RelatedEntityDoesNotExistError_for_improper_brand_id(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(RelatedEntityDoesNotExistError, match="Brand"):
        await refills.create_refill(
            RefillCreate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1,
                ethanol_percent=0.1,
                cost=200.5,
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_create_refill_raises_RelatedEntityDoesNotExistError_for_improper_octane_id(
    testing_session: AsyncSession,
) -> None:
    await setup_dimension_tables(testing_session)
    with pytest.raises(RelatedEntityDoesNotExistError, match="Octane"):
        await refills.create_refill(
            RefillCreate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1000,
                ethanol_percent=0.1,
                cost=200.5,
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_create_refill_regular(testing_session: AsyncSession) -> None:
    await setup_dimension_tables(testing_session)

    result = await refills.create_refill(
        RefillCreate(
            odometer=123,
            liters_filled=3.5,
            brand_id=1,
            octane_id=1,
            ethanol_percent=0.12,
            cost=175,
        ),
        testing_session,
    )

    assert isinstance(result, Refill)
    assert result.id == 1
    assert result.fill_date == date.today()
    assert result.odometer == 123
    assert result.liters_filled == 3.5
    assert result.brand_id == 1
    assert result.octane_id == 1
    assert result.ethanol_percent == 0.12
    assert result.cost == 175


@pytest.mark.asyncio
async def test_find_refill_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await refills.find_refill(404, testing_session)


@pytest.mark.asyncio
async def test_find_refill_regular(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    result = await refills.find_refill(1, testing_session)

    assert isinstance(result, models.Refill)
    assert result.id == 1
    assert result.fill_date == date.today()
    assert result.odometer == 123.5
    assert result.liters_filled == 3.5
    assert result.brand_id == 1
    assert result.octane_id == 1
    assert result.ethanol_percent == Decimal("0.1")
    assert result.cost == 175


@pytest.mark.asyncio
async def test_find_refills_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    result = await refills.find_refills(testing_session)

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_find_refills_regular(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    result = await refills.find_refills(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], models.Refill)
    assert result[0].id == 1
    assert result[0].fill_date == date.today()
    assert result[0].odometer == 123.5
    assert result[0].liters_filled == 3.5
    assert result[0].brand_id == 1
    assert result[0].octane_id == 1
    assert result[0].ethanol_percent == Decimal("0.1")
    assert result[0].cost == 175
    assert isinstance(result[1], models.Refill)
    assert result[1].id == 2
    assert result[1].fill_date == date.today() + timedelta(days=1)
    assert result[1].odometer == Decimal("456.7")
    assert result[1].liters_filled == Decimal("3.7")
    assert result[1].brand_id == 1
    assert result[1].octane_id == 2
    assert result[1].ethanol_percent == 0.0
    assert result[1].cost == 200.5


@pytest.mark.asyncio
async def test_read_refill_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await refills.read_refill(404, testing_session)


@pytest.mark.asyncio
async def test_read_refill_regular(testing_session: AsyncSession) -> None:
    await setup(testing_session)

    result = await refills.read_refill(1, testing_session)

    assert isinstance(result, Refill)
    assert result.id == 1
    assert result.fill_date == date.today()
    assert result.odometer == 123.5
    assert result.liters_filled == 3.5
    assert result.brand_id == 1
    assert result.octane_id == 1
    assert result.ethanol_percent == 0.1
    assert result.cost == 175


@pytest.mark.asyncio
async def test_read_refills_returns_empty_list(
    testing_session: AsyncSession,
) -> None:
    result = await refills.read_refills(testing_session)

    assert isinstance(result, list)
    assert result == []


@pytest.mark.asyncio
async def test_read_refills_regular(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    result = await refills.read_refills(testing_session)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Refill)
    assert result[0].id == 1
    assert result[0].fill_date == date.today()
    assert result[0].odometer == 123.5
    assert result[0].liters_filled == 3.5
    assert result[0].brand_id == 1
    assert result[0].octane_id == 1
    assert result[0].ethanol_percent == 0.1
    assert result[0].cost == 175
    assert isinstance(result[1], Refill)
    assert result[1].id == 2
    assert result[1].fill_date == date.today() + timedelta(days=1)
    assert result[1].odometer == 456.7
    assert result[1].liters_filled == 3.7
    assert result[1].brand_id == 1
    assert result[1].octane_id == 2
    assert result[1].ethanol_percent == 0.0
    assert result[1].cost == 200.5


@pytest.mark.asyncio
async def test_update_refill_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await refills.update_refill(404, RefillUpdate(brand_id=2), testing_session)


@pytest.mark.asyncio
async def test_update_refill_raises_ValidationError(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    with pytest.raises(ValidationError):
        await refills.update_refill(1, RefillUpdate(fill_date=True), testing_session)

    with pytest.raises(ValidationError):
        await refills.update_refill(1, RefillUpdate(odometer="123"), testing_session)

    with pytest.raises(ValidationError):
        await refills.update_refill(
            1, RefillUpdate(odometer=123, liters_filled="1.23"), testing_session
        )

    with pytest.raises(ValidationError):
        await refills.update_refill(
            1,
            RefillUpdate(odometer=123, liters_filled=1.23, brand_id="1"),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.update_refill(
            1,
            RefillUpdate(odometer=123, liters_filled=1.23, brand_id=1, octane_id="1"),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.update_refill(
            1,
            RefillUpdate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1,
                ethanol_percent="0.1",
            ),
            testing_session,
        )

    with pytest.raises(ValidationError):
        await refills.update_refill(
            1,
            RefillUpdate(
                odometer=123,
                liters_filled=1.23,
                brand_id=1,
                octane_id=1,
                ethanol_percent=0.1,
                cost="not much",
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_update_refill_raises_RelatedEntityDoesNotExistError_for_nonexistent_brand(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    with pytest.raises(RelatedEntityDoesNotExistError):
        await refills.update_refill(
            2,
            RefillUpdate(odometer=789, brand_id=1000, ethanol_percent=0.05),
            testing_session,
        )


@pytest.mark.asyncio
async def test_update_refill_raises_RelatedEntityDoesNotExistError_for_nonexistent_octane(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    with pytest.raises(RelatedEntityDoesNotExistError):
        await refills.update_refill(
            2,
            RefillUpdate(
                odometer=789, brand_id=1, octane_id=1000, ethanol_percent=0.05
            ),
            testing_session,
        )


@pytest.mark.asyncio
async def test_update_refill_regular(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    result = await refills.update_refill(
        2, RefillUpdate(odometer=789, brand_id=2, ethanol_percent=0.05), testing_session
    )

    assert isinstance(result, Refill)
    assert result.id == 2
    assert result.fill_date == date.today() + timedelta(days=1)
    assert result.odometer == 789
    assert result.liters_filled == 3.7
    assert result.brand_id == 2
    assert result.octane_id == 2
    assert result.ethanol_percent == 0.05
    assert result.cost == 200.5


@pytest.mark.asyncio
async def test_delete_refill_raises_EntityDoesNotExistError(
    testing_session: AsyncSession,
) -> None:
    with pytest.raises(EntityDoesNotExistError):
        await refills.delete_refill(1, testing_session)


@pytest.mark.asyncio
async def test_delete_refill_regular(
    testing_session: AsyncSession,
) -> None:
    await setup(testing_session)

    result = await refills.delete_refill(1, testing_session)
    table_contents = await refills.read_refills(testing_session)

    assert isinstance(result, Refill)
    assert result.id == 1
    assert result.odometer == 123.5
    assert result.liters_filled == 3.5
    assert result.brand_id == 1
    assert result.octane_id == 1
    assert result.ethanol_percent == 0.1
    assert result.cost == 175

    assert len(table_contents) == 1
    assert table_contents[0].id == 2
