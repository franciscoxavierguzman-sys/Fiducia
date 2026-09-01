from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.forecasting.evaluation import ALLOWED_HORIZONS, FORECAST_VERSION, chronological_split, evaluate_models, forecast_future, residual_intervals, walk_forward_predictions
from app.forecasting.preprocessing import FORECASTING_DATASET_PATH, PROCESSED_DATASET_PATH, dataset_hash, prepare_forecasting_dataset


TARGETS = ["transaction_count", "transaction_amount_usd"]


def train_forecast_models(seed: int = 42) -> dict:
    if not FORECASTING_DATASET_PATH.exists():
        prepare_forecasting_dataset()
    series = pd.read_csv(FORECASTING_DATASET_PATH, parse_dates=["period"])
    artifact_dir = PROJECT_ROOT / "ml" / "artifacts" / "forecasting"
    report_dir = PROJECT_ROOT / "reports" / "forecasting"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "model_name": "FIDUCIA Remittance Forecast",
        "version": FORECAST_VERSION,
        "data_type": "synthetic",
        "granularity": "weekly",
        "forecast_horizons": sorted(ALLOWED_HORIZONS),
        "dataset": str(FORECASTING_DATASET_PATH),
        "dataset_hash": dataset_hash(FORECASTING_DATASET_PATH),
        "source_dataset": str(PROCESSED_DATASET_PATH),
        "source_dataset_hash": dataset_hash(PROCESSED_DATASET_PATH),
        "seed": seed,
        "trained_at": datetime.now(UTC).isoformat(),
        "library_versions": {"python": platform.python_version(), "pandas": pd.__version__},
        "targets": {},
    }
    metrics_report = {
        "version": FORECAST_VERSION,
        "split_strategy": "chronological train/validation/test",
        "selection_rule": "selected by validation WAPE, with TEST used only once for final reporting",
        "targets": {},
    }
    artifacts = {}
    for target in TARGETS:
        results, selected_model = evaluate_models(series, target)
        train, validation, test = chronological_split(series)
        selected = next(item for item in results if item.name == selected_model)
        combined = pd.concat([train, validation], ignore_index=True)
        validation_pred = walk_forward_predictions(train[target].tolist(), validation[target].tolist(), selected_model, 4)
        intervals = residual_intervals(validation[target].to_numpy(dtype=float), validation_pred)
        future = forecast_future(series[target].tolist(), series["period"], selected_model, 12, intervals)
        target_artifact = {
            "model_version": FORECAST_VERSION,
            "target": target,
            "granularity": "weekly",
            "selected_model": selected_model,
            "history": series[["period", target]].assign(period=series["period"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")).to_dict(orient="records"),
            "interval_widths": intervals,
            "last_training_period": series["period"].max().isoformat(),
            "minimum_periods_required": 52,
        }
        artifacts[target] = target_artifact
        joblib.dump(target_artifact, artifact_dir / f"{target}_forecast.joblib")
        metadata["targets"][target] = {
            "selected_model": selected_model,
            "training_period": {"start": train["period"].min().isoformat(), "end": train["period"].max().isoformat(), "periods": len(train)},
            "validation_period": {"start": validation["period"].min().isoformat(), "end": validation["period"].max().isoformat(), "periods": len(validation)},
            "test_period": {"start": test["period"].min().isoformat(), "end": test["period"].max().isoformat(), "periods": len(test)},
            "features": ["lagged target history only", "week index for optional ML candidate"],
            "parameters": {"seasonal_period": 4, "minimum_periods_required": 52},
            "metrics": selected.test,
            "forecast": future,
        }
        metrics_report["targets"][target] = {
            "selected_model": selected_model,
            "comparison": [
                {
                    "model": item.name,
                    "complexity": item.complexity,
                    "training_time_seconds": item.training_time_seconds,
                    "validation": item.validation,
                    "test": item.test,
                    "selected": item.selected,
                }
                for item in results
            ],
        }
    (artifact_dir / "forecast_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (artifact_dir / "forecast_metrics.json").write_text(json.dumps(metrics_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "model_comparison.json").write_text(json.dumps(metrics_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "backtest_results.json").write_text(json.dumps(metrics_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "future_forecast.json").write_text(json.dumps({target: metadata["targets"][target]["forecast"] for target in TARGETS}, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"metadata": metadata, "metrics": metrics_report, "artifacts": list(artifacts)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = train_forecast_models(args.seed)
    print(json.dumps({"version": result["metadata"]["version"], "targets": result["artifacts"]}, indent=2))


if __name__ == "__main__":
    main()
