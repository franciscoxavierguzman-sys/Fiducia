from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    target: Mapped[str] = mapped_column(String(80), nullable=False)
    granularity: Mapped[str] = mapped_column(String(30), nullable=False)
    horizon: Mapped[int] = mapped_column(nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    training_cutoff: Mapped[str] = mapped_column(String(40), nullable=False)
    parameters_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    values = relationship("ForecastValue", back_populates="run")


class ForecastValue(Base):
    __tablename__ = "forecast_values"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    forecast_run_id: Mapped[int] = mapped_column(ForeignKey("forecast_runs.id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    predicted_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    lower_80: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    upper_80: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    lower_95: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    upper_95: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    run = relationship("ForecastRun", back_populates="values")
