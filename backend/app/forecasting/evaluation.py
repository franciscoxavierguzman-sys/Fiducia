from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor


MIN_PERIODS_REQUIRED = 52
FORECAST_VERSION = "remittance-forecast-v1"
ALLOWED_TARGETS = {"transaction_count", "transaction_amount_usd"}
ALLOWED_GRANULARITIES = {"weekly"}
ALLOWED_HORIZONS = {4, 8, 12}


@dataclass
class ForecastModelResult:
    name: str
    complexity: str
    validation: dict
    test: dict
    training_time_seconds: float
    selected: bool = False


def chronological_split(series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    total = len(series)
    train_end = int(total * 0.70)
    validation_end = int(total * 0.85)
    return series.iloc[:train_end].copy(), series.iloc[train_end:validation_end].copy(), series.iloc[validation_end:].copy()


def evaluate_models(series: pd.DataFrame, target: str, seasonal_period: int = 4) -> tuple[list[ForecastModelResult], str]:
    if len(series) < MIN_PERIODS_REQUIRED:
        raise ValueError("INSUFFICIENT_HISTORY")
    train, validation, test = chronological_split(series)
    candidates = ["Naive", "Seasonal Naive", "Moving Average 4", "Moving Average 8", "HistGradientBoosting"]
    results: list[ForecastModelResult] = []
    for name in candidates:
        start = time.perf_counter()
        validation_pred = walk_forward_predictions(train[target].tolist(), validation[target].tolist(), name, seasonal_period)
        validation_metrics = metrics(validation[target].to_numpy(dtype=float), validation_pred)
        combined_history = pd.concat([train, validation], ignore_index=True)
        test_pred = walk_forward_predictions(combined_history[target].tolist(), test[target].tolist(), name, seasonal_period)
        test_metrics = metrics(test[target].to_numpy(dtype=float), test_pred)
        results.append(
            ForecastModelResult(
                name=name,
                complexity="baseline" if name in {"Naive", "Seasonal Naive"} else "simple_ml" if name == "HistGradientBoosting" else "statistical_baseline",
                validation=validation_metrics,
                test=test_metrics,
                training_time_seconds=round(time.perf_counter() - start, 4),
            )
        )
    selected = min(results, key=lambda item: (item.validation["wape"], item.validation["mae"], 0 if item.complexity != "simple_ml" else 1))
    selected.selected = True
    return results, selected.name


def walk_forward_predictions(history_values: list[float], actual_values: list[float], model_name: str, seasonal_period: int) -> np.ndarray:
    history = [float(value) for value in history_values]
    predictions = []
    for actual in actual_values:
        predictions.append(predict_next(history, model_name, seasonal_period))
        history.append(float(actual))
    return np.asarray(predictions, dtype=float)


def predict_next(history: list[float], model_name: str, seasonal_period: int = 4) -> float:
    if not history:
        return 0.0
    if model_name == "Naive":
        return max(0.0, history[-1])
    if model_name == "Seasonal Naive":
        return max(0.0, history[-seasonal_period] if len(history) >= seasonal_period else history[-1])
    if model_name == "Moving Average 4":
        return max(0.0, float(np.mean(history[-4:])))
    if model_name == "Moving Average 8":
        return max(0.0, float(np.mean(history[-8:])))
    if model_name == "HistGradientBoosting":
        return max(0.0, gradient_boosting_next(history))
    raise ValueError(f"Modelo no soportado: {model_name}")


def gradient_boosting_next(history: list[float]) -> float:
    if len(history) < 16:
        return float(np.mean(history[-4:]))
    data = []
    target = []
    for index in range(8, len(history)):
        lagged = history[:index]
        data.append(
            [
                lagged[-1],
                lagged[-2],
                lagged[-4],
                lagged[-8],
                float(np.mean(lagged[-4:])),
                float(np.mean(lagged[-8:])),
                float(np.std(lagged[-4:])),
                index % 52,
            ]
        )
        target.append(history[index])
    model = HistGradientBoostingRegressor(max_iter=80, learning_rate=0.05, max_leaf_nodes=12, random_state=42)
    model.fit(np.asarray(data), np.asarray(target))
    current = [
        history[-1],
        history[-2],
        history[-4],
        history[-8],
        float(np.mean(history[-4:])),
        float(np.mean(history[-8:])),
        float(np.std(history[-4:])),
        len(history) % 52,
    ]
    return float(model.predict([current])[0])


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    actual = actual.astype(float)
    predicted = np.maximum(0, predicted.astype(float))
    errors = actual - predicted
    denominator = float(np.sum(np.abs(actual)))
    non_zero = actual != 0
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(math.sqrt(np.mean(errors**2))),
        "wape": float(np.sum(np.abs(errors)) / denominator) if denominator else None,
        "smape": float(np.mean(2 * np.abs(errors[non_zero]) / (np.abs(actual[non_zero]) + np.abs(predicted[non_zero])))) if non_zero.any() else None,
    }


def residual_intervals(actual: np.ndarray, predicted: np.ndarray) -> dict:
    residuals = actual.astype(float) - predicted.astype(float)
    abs_residuals = np.abs(residuals)
    return {"q80": float(np.quantile(abs_residuals, 0.80)), "q95": float(np.quantile(abs_residuals, 0.95))}


def forecast_future(history_values: list[float], periods: pd.Series, model_name: str, horizon: int, interval_widths: dict) -> list[dict]:
    history = [float(value) for value in history_values]
    last_period = pd.to_datetime(periods.iloc[-1])
    rows = []
    for step in range(1, horizon + 1):
        predicted = predict_next(history, model_name)
        history.append(predicted)
        period = last_period + pd.Timedelta(weeks=step)
        rows.append(
            {
                "period": period.isoformat(),
                "predicted": round(float(predicted), 2),
                "lower_80": round(max(0.0, float(predicted) - interval_widths["q80"]), 2),
                "upper_80": round(float(predicted) + interval_widths["q80"], 2),
                "lower_95": round(max(0.0, float(predicted) - interval_widths["q95"]), 2),
                "upper_95": round(float(predicted) + interval_widths["q95"], 2),
            }
        )
    return rows
