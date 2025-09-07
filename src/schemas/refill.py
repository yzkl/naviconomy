from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RefillBase(BaseModel):
    fill_date: Optional[date] = None
    odometer: float
    liters_filled: float
    brand_id: int
    octane_id: int
    ethanol_percent: float
    cost: float

    model_config = ConfigDict(from_attributes=True, strict=True)


class RefillCreate(RefillBase):
    pass


class RefillUpdate(RefillBase):
    odometer: Optional[float] = None
    liters_filled: Optional[float] = None
    brand_id: Optional[int] = None
    octane_id: Optional[int] = None
    ethanol_percent: Optional[float] = None
    cost: Optional[float] = None


class Refill(RefillBase):
    id: int