from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RemittanceCorridor(Base):
    __tablename__ = "remittance_corridors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    origin_country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False, index=True)
    destination_country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False, index=True)
    origin_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    estimated_delivery: Mapped[str] = mapped_column(String(120), nullable=False, default="Disponible en minutos")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    origin_country = relationship("Country", foreign_keys=[origin_country_id])
    destination_country = relationship("Country", foreign_keys=[destination_country_id])
