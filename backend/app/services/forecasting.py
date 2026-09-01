from __future__ import annotations

import json
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.forecasting.evaluation import ALLOWED_GRANULARITIES, ALLOWED_HORIZONS, ALLOWED_TARGETS, forecast_future
from app.forecasting.preprocessing import FORECASTING_DATASET_PATH
from app.models.forecast import ForecastRun, ForecastValue


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FORECAST_ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts" / "forecasting"
FORECAST_METADATA_PATH = FORECAST_ARTIFACT_DIR / "forecast_metadata.json"
FORECAST_METRICS_PATH = FORECAST_ARTIFACT_DIR / "forecast_metrics.json"
TEMPORAL_AUDIT_PATH = PROJECT_ROOT / "reports" / "forecasting" / "temporal_audit.json"


def validate_forecast_params(target: str, horizon: int, granularity: str = "weekly") -> None:
    if target not in ALLOWED_TARGETS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "INVALID_TARGET", "message": "Target no permitido"})
    if horizon not in ALLOWED_HORIZONS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "INVALID_HORIZON", "message": "Horizonte no permitido"})
    if granularity not in ALLOWED_GRANULARITIES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "INVALID_GRANULARITY", "message": "Granularidad no permitida"})


def get_forecast_model_info() -> dict[str, Any]:
    if not FORECAST_METADATA_PATH.exists():
        return {"available": False, "message": "Modelo de forecasting no entrenado."}
    metadata = _load_metadata()
    return {"available": True, **metadata}


def get_forecast_summary() -> dict[str, Any]:
    metadata = _load_metadata()
    count_forecast = generate_forecast("transaction_count", 4, persist=False)
    amount_forecast = generate_forecast("transaction_amount_usd", 4, persist=False)
    audit = _load_json(TEMPORAL_AUDIT_PATH)
    return {
        "model_version": metadata["version"],
        "go_decision": audit.get("go_decision", "CONDITIONAL"),
        "records": int(audit.get("records", 0)),
        "weeks_covered": int(audit.get("weeks_covered", 0)),
        "months_covered": int(audit.get("months_covered", 0)),
        "latest_period": metadata["targets"]["transaction_count"]["test_period"]["end"],
        "next_4_weeks_count": sum(Decimal(str(item["predicted"])) for item in count_forecast["forecast"]),
        "next_4_weeks_amount_usd": sum(Decimal(str(item["predicted"])) for item in amount_forecast["forecast"]),
        "count_wape": metadata["targets"]["transaction_count"]["metrics"]["wape"],
        "amount_wape": metadata["targets"]["transaction_amount_usd"]["metrics"]["wape"],
        "drift_status": drift_status(),
        "data_type": metadata["data_type"],
    }


def generate_forecast(target: str, horizon: int, granularity: str = "weekly", db: Session | None = None, persist: bool = False) -> dict[str, Any]:
    validate_forecast_params(target, horizon, granularity)
    artifact = _load_target_artifact(target)
    metadata = _load_metadata()
    target_meta = metadata["targets"][target]
    history = artifact["history"]
    series = pd.DataFrame(history)
    series["period"] = pd.to_datetime(series["period"], utc=True)
    history_values = [float(item[target]) for item in history]
    forecast = forecast_future(history_values, series["period"], artifact["selected_model"], horizon, artifact["interval_widths"])
    response = {
        "model_version": metadata["version"],
        "selected_model": artifact["selected_model"],
        "target": target,
        "granularity": granularity,
        "horizon": horizon,
        "currency": "USD equivalent" if target == "transaction_amount_usd" else None,
        "historical": [{"period": item["period"], "value": Decimal(str(item[target]))} for item in history[-24:]],
        "forecast": forecast,
        "metrics": target_meta["metrics"],
        "data_type": metadata["data_type"],
        "interval_method": "intervalos 80/95 basados en cuantiles absolutos de residuales validation",
        "warning": "Pronostico experimental basado en datos sinteticos; no garantiza resultados futuros.",
    }
    if persist and db is not None:
        persist_forecast_run(db, response, artifact["last_training_period"])
    return response


def get_corridor_forecasts(horizon: int = 4) -> list[dict[str, Any]]:
    validate_forecast_params("transaction_count", horizon, "weekly")
    top_path = FORECASTING_DATASET_PATH.parent / "top_corridors.csv"
    if not top_path.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "FORECAST_DATA_NOT_AVAILABLE", "message": "Dataset de corredores no disponible"})
    metadata = _load_metadata()
    count_weekly = sum(Decimal(str(item["predicted"])) for item in metadata["targets"]["transaction_count"]["forecast"][:horizon])
    amount_weekly = sum(Decimal(str(item["predicted"])) for item in metadata["targets"]["transaction_amount_usd"]["forecast"][:horizon])
    rows = pd.read_csv(top_path).to_dict(orient="records")
    total_volume = sum(row["transaction_count"] for row in rows) or 1
    total_amount = sum(row["transaction_amount_usd"] for row in rows) or 1
    return [
        {
            "corridor": row["corridor"],
            "historical_volume": int(row["transaction_count"]),
            "historical_amount_usd": Decimal(str(round(row["transaction_amount_usd"], 2))),
            "forecast_volume_next_4w": Decimal(str(round(float(count_weekly) * row["transaction_count"] / total_volume, 2))),
            "forecast_amount_usd_next_4w": Decimal(str(round(float(amount_weekly) * row["transaction_amount_usd"] / total_amount, 2))),
            "status": "OK",
        }
        for row in rows
    ]


def persist_forecast_run(db: Session, response: dict[str, Any], training_cutoff: str) -> None:
    run = ForecastRun(
        model_version=response["model_version"],
        target=response["target"],
        granularity=response["granularity"],
        horizon=response["horizon"],
        training_cutoff=training_cutoff,
        parameters_json={"selected_model": response["selected_model"], "interval_method": response["interval_method"]},
    )
    db.add(run)
    db.flush()
    for item in response["forecast"]:
        db.add(
            ForecastValue(
                forecast_run_id=run.id,
                period=item["period"],
                predicted_value=Decimal(str(item["predicted"])),
                lower_80=Decimal(str(item["lower_80"])),
                upper_80=Decimal(str(item["upper_80"])),
                lower_95=Decimal(str(item["lower_95"])),
                upper_95=Decimal(str(item["upper_95"])),
            )
        )
    db.commit()


def drift_status() -> str:
    metadata = _load_metadata()
    count_wape = float(metadata["targets"]["transaction_count"]["metrics"]["wape"])
    amount_wape = float(metadata["targets"]["transaction_amount_usd"]["metrics"]["wape"])
    return "ATTENTION" if count_wape > 0.20 or amount_wape > 0.25 else "NORMAL"


@lru_cache(maxsize=1)
def _load_metadata() -> dict[str, Any]:
    if not FORECAST_METADATA_PATH.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "FORECAST_MODEL_NOT_AVAILABLE", "message": "Modelo de forecasting no disponible"})
    return json.loads(FORECAST_METADATA_PATH.read_text(encoding="utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def _load_target_artifact(target: str) -> dict[str, Any]:
    path = FORECAST_ARTIFACT_DIR / f"{target}_forecast.joblib"
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "FORECAST_ARTIFACT_NOT_AVAILABLE", "message": "Artefacto de forecasting no disponible"})
    return joblib.load(path)
