from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    period: str
    predicted: Decimal
    lower_80: Decimal | None = None
    upper_80: Decimal | None = None
    lower_95: Decimal | None = None
    upper_95: Decimal | None = None


class HistoricalPoint(BaseModel):
    period: str
    value: Decimal


class ForecastResponse(BaseModel):
    model_version: str
    selected_model: str
    target: str
    granularity: str
    horizon: int
    currency: str | None = None
    historical: list[HistoricalPoint]
    forecast: list[ForecastPoint]
    metrics: dict[str, Any]
    data_type: str
    interval_method: str
    warning: str | None = None


class ForecastModelInfo(BaseModel):
    available: bool
    model_name: str | None = None
    version: str | None = None
    granularity: str | None = None
    forecast_horizons: list[int] = []
    targets: dict[str, Any] = {}
    data_type: str | None = None
    message: str | None = None


class ForecastSummary(BaseModel):
    model_version: str
    go_decision: str
    records: int
    weeks_covered: int
    months_covered: int
    latest_period: str
    next_4_weeks_count: Decimal
    next_4_weeks_amount_usd: Decimal
    count_wape: float
    amount_wape: float
    drift_status: str
    data_type: str


class ForecastCorridorItem(BaseModel):
    corridor: str
    historical_volume: int
    historical_amount_usd: Decimal
    forecast_volume_next_4w: Decimal
    forecast_amount_usd_next_4w: Decimal
    status: str
