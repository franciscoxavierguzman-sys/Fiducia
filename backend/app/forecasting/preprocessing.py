from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pandas as pd

from app.analytics.constants import EXCHANGE_RATES_TO_USD


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "remittances_analytics.csv"
FORECASTING_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "forecasting"
FORECASTING_DATASET_PATH = FORECASTING_DATA_DIR / "weekly_remittances_forecasting.csv"


def dataset_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_remittance_dataset(path: Path = PROCESSED_DATASET_PATH) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["created_at"])
    required = {"created_at", "source_amount", "source_currency", "origin_country", "destination_country"}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Dataset incompleto para forecasting. Faltan columnas: {missing}")
    data["created_at"] = pd.to_datetime(data["created_at"], utc=True)
    data["amount_usd_equivalent"] = data.apply(
        lambda row: float(row["source_amount"]) * float(EXCHANGE_RATES_TO_USD.get(str(row["source_currency"]), 0)),
        axis=1,
    )
    data["corridor"] = data["origin_country"].astype(str) + " -> " + data["destination_country"].astype(str)
    return data.sort_values("created_at").reset_index(drop=True)


def build_weekly_series(data: pd.DataFrame, corridor: str | None = None) -> pd.DataFrame:
    frame = data if corridor is None else data[data["corridor"] == corridor]
    if frame.empty:
        return pd.DataFrame(columns=["period", "transaction_count", "transaction_amount_usd"])
    weekly = (
        frame.set_index("created_at")
        .resample("W-MON", label="left", closed="left")
        .agg(transaction_count=("source_amount", "count"), transaction_amount_usd=("amount_usd_equivalent", "sum"))
        .reset_index()
        .rename(columns={"created_at": "period"})
    )
    full_periods = pd.date_range(weekly["period"].min(), weekly["period"].max(), freq="W-MON", tz="UTC")
    weekly = weekly.set_index("period").reindex(full_periods, fill_value=0).rename_axis("period").reset_index()
    weekly["transaction_count"] = weekly["transaction_count"].astype(int)
    weekly["transaction_amount_usd"] = weekly["transaction_amount_usd"].round(2)
    return weekly


def prepare_forecasting_dataset(source_path: Path = PROCESSED_DATASET_PATH, output_path: Path = FORECASTING_DATASET_PATH) -> dict:
    data = load_remittance_dataset(source_path)
    weekly = build_weekly_series(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_csv(output_path, index=False)
    corridors = (
        data.groupby("corridor")
        .agg(transaction_count=("source_amount", "count"), transaction_amount_usd=("amount_usd_equivalent", "sum"))
        .sort_values(["transaction_count", "transaction_amount_usd"], ascending=False)
        .head(5)
        .reset_index()
    )
    corridors.to_csv(output_path.parent / "top_corridors.csv", index=False)
    return {
        "source_dataset": str(source_path),
        "source_hash": dataset_hash(source_path),
        "output_dataset": str(output_path),
        "output_hash": dataset_hash(output_path),
        "records": int(len(weekly)),
        "start_period": weekly["period"].min().isoformat(),
        "end_period": weekly["period"].max().isoformat(),
        "top_corridors": corridors.to_dict(orient="records"),
    }
