from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Brand(Base):
    __tablename__ = "dim_brands"

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(32), unique=True)

    refills = relationship("Refill", back_populates="brand")
    