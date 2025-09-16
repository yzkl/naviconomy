from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(32), unique=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class UserBase(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True, strict=True)


class RegisterUserRequest(UserBase):
    password: SecretStr


class User(UserBase):
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
