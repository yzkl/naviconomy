from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Octane(Base):
    __tablename__ = "dim_octanes"

    id: Mapped[Optional[int]] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, unique=True)

    refills = relationship("Refill", back_populates="octane")
