from decimal import Decimal

from pydantic import BaseModel


class AnalyticsMetric(BaseModel):
    label: str
    value: Decimal
    currency: str | None = None


class AnalyticsDistributionItem(BaseModel):
    label: str
    count: int
    amount: Decimal | None = None
    currency: str | None = None


class AnalyticsTimeSeriesPoint(BaseModel):
    period: str
    count: int
    volume_usd_equivalent: Decimal
    commission_usd_equivalent: Decimal


class AnalyticsSummary(BaseModel):
    total_remittances: int
    volume_usd_equivalent: Decimal
    commission_usd_equivalent: Decimal
    average_ticket_usd_equivalent: Decimal
    top_corridor: str | None
    synthetic_fraud_cases: int

