from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Refill(Base):
    __tablename__ = "fct_refills"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    fill_date: Mapped[Optional[date]] = mapped_column(
        Date, default=lambda: date.today()
    )
    odometer: Mapped[float] = mapped_column(Numeric(1))
    liters_filled: Mapped[float] = mapped_column(Numeric(2))
    brand_id: Mapped[int] = mapped_column(ForeignKey("dim_brands.id"))
    octane_id: Mapped[int] = mapped_column(ForeignKey("dim_octanes.id"))
    ethanol_percent: Mapped[float] = mapped_column(Numeric(2))
    cost: Mapped[float] = mapped_column(Numeric(2))

    brand = relationship("Brand", back_populates="refills")
    octane = relationship("Octane", back_populates="refills")
