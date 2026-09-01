from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    iso_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    currency_symbol: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_origin_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_destination_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
