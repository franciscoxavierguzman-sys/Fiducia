from __future__ import annotations

import csv
import io
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.bi.calculations import calculate_corridors, calculate_customers, calculate_operations, calculate_risk, calculate_trends
from app.bi.comparisons import compare_overview
from app.bi.filters import BIFilters
from app.bi.insights import build_executive_insights
from app.bi.kpis import get_kpi_catalog
from app.services.forecasting import get_forecast_summary


def get_bi_kpis() -> list[dict]:
    return get_kpi_catalog()


def get_bi_overview(db: Session, filters: BIFilters) -> dict:
    return compare_overview(db, filters)


def get_bi_trends(db: Session, filters: BIFilters, granularity: str = "week") -> list[dict]:
    return calculate_trends(db, filters, granularity)


def get_bi_corridors(db: Session, filters: BIFilters) -> list[dict]:
    return calculate_corridors(db, filters)


def get_bi_customers(db: Session, filters: BIFilters) -> dict:
    return calculate_customers(db, filters)


def get_bi_operations(db: Session, filters: BIFilters) -> dict:
    return calculate_operations(db, filters)


def get_bi_risk(db: Session, filters: BIFilters) -> dict:
    return calculate_risk(db, filters)


def get_bi_forecast() -> dict:
    summary = get_forecast_summary()
    return {
        "model_version": summary["model_version"],
        "go_decision": summary["go_decision"],
        "horizon": 4,
        "next_4_weeks_count": summary["next_4_weeks_count"],
        "next_4_weeks_amount_usd": summary["next_4_weeks_amount_usd"],
        "drift_status": summary["drift_status"],
        "data_type": summary["data_type"],
    }


def get_executive_summary(db: Session, filters: BIFilters) -> dict:
    overview = compare_overview(db, filters)
    corridors = calculate_corridors(db, filters)
    operations = calculate_operations(db, filters)
    risk = calculate_risk(db, filters)
    forecast = get_bi_forecast()
    return {
        "period": {"date_from": filters.date_from, "date_to": filters.date_to},
        "filters": {
            "origin_country": filters.origin_country,
            "destination_country": filters.destination_country,
            "currency": filters.currency,
            "status": filters.status,
        },
        "highlights": build_executive_insights(overview, corridors, operations, risk, forecast),
        "attention_points": [item for item in build_executive_insights(overview, corridors, operations, risk, forecast) if item["priority"] == "ATTENTION"],
        "forecast_outlook": forecast,
    }


def export_kpis_csv(db: Session, filters: BIFilters) -> str:
    overview = compare_overview(db, filters)
    rows = [{"kpi": key, "value": value} for key, value in overview["current"].items()]
    return _csv_from_rows(rows, ["kpi", "value"])


def export_corridors_csv(db: Session, filters: BIFilters) -> str:
    rows = get_bi_corridors(db, filters)
    fields = ["corridor", "remittance_count", "total_amount_usd_equivalent", "average_ticket_usd_equivalent", "commission_revenue_usd_equivalent", "completion_rate"]
    return _csv_from_rows(rows, fields)


def _csv_from_rows(rows: list[dict[str, Any]], fieldnames: list[str]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})
    return output.getvalue()


def _csv_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    return value
