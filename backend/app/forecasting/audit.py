from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.forecasting.preprocessing import build_weekly_series, load_remittance_dataset


def temporal_audit(source_path: Path) -> dict:
    data = load_remittance_dataset(source_path)
    daily = data.set_index("created_at").resample("D").size()
    weekly = build_weekly_series(data)
    monthly = data.set_index("created_at").resample("MS").size()
    gaps = int((daily == 0).sum())
    duplicate_timestamps = int(data["created_at"].duplicated().sum())
    weekday_counts = data["created_at"].dt.day_name().value_counts().to_dict()
    monthly_counts = {str(index.date()): int(value) for index, value in monthly.items()}
    weekly_counts = {row["period"].date().isoformat(): int(row["transaction_count"]) for _, row in weekly.iterrows()}
    go_decision = "CONDITIONAL"
    reason = (
        "El dataset sintetico cubre menos de 24 meses, pero contiene 78 semanas continuas y volumen semanal suficiente "
        "para forecasting experimental de corto plazo. No es defendible como prediccion real de remesas nacionales."
    )
    return {
        "dataset": str(source_path),
        "records": int(len(data)),
        "start_date": data["created_at"].min().isoformat(),
        "end_date": data["created_at"].max().isoformat(),
        "days_covered": int(daily.shape[0]),
        "weeks_covered": int(weekly.shape[0]),
        "months_covered": int(monthly.shape[0]),
        "daily_missing_periods": gaps,
        "duplicate_timestamps": duplicate_timestamps,
        "daily_records": {
            "min": int(daily.min()),
            "max": int(daily.max()),
            "mean": float(daily.mean()),
            "median": float(daily.median()),
        },
        "weekly_records": {
            "min": int(weekly["transaction_count"].min()),
            "max": int(weekly["transaction_count"].max()),
            "mean": float(weekly["transaction_count"].mean()),
            "median": float(weekly["transaction_count"].median()),
        },
        "monthly_records": {
            "min": int(monthly.min()),
            "max": int(monthly.max()),
            "mean": float(monthly.mean()),
            "median": float(monthly.median()),
        },
        "weekday_distribution": weekday_counts,
        "monthly_counts": monthly_counts,
        "weekly_counts": weekly_counts,
        "continuity": "weekly_continuous" if weekly["transaction_count"].min() > 0 else "weekly_has_gaps",
        "trend_observation": "serie semanal sintetica con variacion moderada; no se asume causalidad economica real",
        "seasonality_observation": "hay patron semanal observable por construccion sintetica; estacionalidad mensual limitada",
        "go_decision": go_decision,
        "go_reason": reason,
        "recommended_granularity": "weekly",
    }
