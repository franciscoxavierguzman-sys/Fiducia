from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.risk.aggregator import RISK_BAND_THRESHOLDS, RISK_ENGINE_WEIGHTS
from app.risk.rules import evaluate_rules
from ml.config import DATASET_PATH, FEATURES, TARGET
from ml.training.train import stratified_split
from scripts.train_anomaly_model import ANOMALY_FEATURES, transform_scores


def evaluate_risk_engine(dataset_path: Path = DATASET_PATH) -> dict:
    data = pd.read_csv(dataset_path)
    _, x_validation, x_test, _, y_validation, y_test = stratified_split(data, 42)
    fraud_artifact = joblib.load(PROJECT_ROOT / "ml" / "artifacts" / "fraud_model.joblib")
    anomaly_artifact = joblib.load(PROJECT_ROOT / "ml" / "artifacts" / "anomaly_model.joblib")

    validation_signals = build_signals(x_validation, fraud_artifact, anomaly_artifact)
    test_signals = build_signals(x_test, fraud_artifact, anomaly_artifact)
    operational_threshold = RISK_BAND_THRESHOLDS["high"]
    previous_threshold = 50.0
    ml_operational_threshold = float(fraud_artifact["threshold"]) * 100
    strategies = {
        "ML only": ({"ml": 1.0}, ml_operational_threshold),
        "Rules only": ({"rules": 1.0}, previous_threshold),
        "Anomaly only": ({"anomaly": 1.0}, previous_threshold),
        "ML + Rules": ({"ml": 0.60, "rules": 0.40}, previous_threshold),
        "ML + Anomaly": ({"ml": 0.70, "anomaly": 0.30}, previous_threshold),
        "Rules + Anomaly": ({"rules": 0.60, "anomaly": 0.40}, previous_threshold),
        "Full Risk Engine": (RISK_ENGINE_WEIGHTS, operational_threshold),
    }
    validation_results = {name: evaluate_strategy(validation_signals, y_validation, weights, threshold) for name, (weights, threshold) in strategies.items()}
    test_results = {name: evaluate_strategy(test_signals, y_test, weights, threshold) for name, (weights, threshold) in strategies.items()}
    current_score_validation = combine_scores(validation_signals, RISK_ENGINE_WEIGHTS)
    current_score_test = combine_scores(test_signals, RISK_ENGINE_WEIGHTS)
    report = {
        "methodology": "Weights are a baseline heuristico inicial. HIGH >= 40 is an authorized operational Decision Support threshold. TEST is reported only for final quantification.",
        "risk_engine_version": "risk-engine-v1.1",
        "weights": RISK_ENGINE_WEIGHTS,
        "weights_status": "baseline heuristico inicial",
        "risk_band_thresholds": RISK_BAND_THRESHOLDS,
        "bands_status": "thresholds operativos de Decision Support",
        "high_threshold_comparison": {
            "validation_high_50": evaluate_strategy(validation_signals, y_validation, RISK_ENGINE_WEIGHTS, previous_threshold),
            "validation_high_40": evaluate_strategy(validation_signals, y_validation, RISK_ENGINE_WEIGHTS, operational_threshold),
            "test_high_50": evaluate_strategy(test_signals, y_test, RISK_ENGINE_WEIGHTS, previous_threshold),
            "test_high_40": evaluate_strategy(test_signals, y_test, RISK_ENGINE_WEIGHTS, operational_threshold),
        },
        "band_counts": {
            "validation": band_counts(current_score_validation),
            "test": band_counts(current_score_test),
        },
        "validation": validation_results,
        "test": test_results,
    }
    out_dir = PROJECT_ROOT / "reports" / "risk_engine"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ablation_results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def build_signals(frame: pd.DataFrame, fraud_artifact: dict, anomaly_artifact: dict) -> dict[str, np.ndarray]:
    ml_probability = fraud_artifact["pipeline"].predict_proba(frame[FEATURES])[:, 1]
    anomaly_decision = anomaly_artifact["pipeline"].decision_function(frame[ANOMALY_FEATURES])
    calibration = anomaly_artifact["calibration"]
    anomaly_score = transform_scores(anomaly_decision, calibration["lower_decision_score"], calibration["upper_decision_score"])
    rule_score = np.asarray([evaluate_rules(row.to_dict())["rule_score"] for _, row in frame.iterrows()], dtype=float)
    return {"ml": ml_probability * 100, "rules": rule_score, "anomaly": anomaly_score}


def evaluate_strategy(signals: dict[str, np.ndarray], labels, weights: dict[str, float], high_threshold: float) -> dict:
    score = combine_scores(signals, weights)
    predictions = (score >= high_threshold).astype(int)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    return {
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(labels, score)),
        "pr_auc": float(average_precision_score(labels, score)),
        "confusion_matrix": matrix.tolist(),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "score_percentiles": {str(p): float(np.percentile(score, p)) for p in [5, 25, 50, 75, 90, 95, 99]},
    }


def combine_scores(signals: dict[str, np.ndarray], weights: dict[str, float]) -> np.ndarray:
    total_weight = sum(weights.values())
    return sum(signals[name] * (weight / total_weight) for name, weight in weights.items())


def band_counts(score: np.ndarray) -> dict[str, int]:
    low = int(np.sum(score < RISK_BAND_THRESHOLDS["medium"]))
    medium = int(np.sum((score >= RISK_BAND_THRESHOLDS["medium"]) & (score < RISK_BAND_THRESHOLDS["high"])))
    high = int(np.sum(score >= RISK_BAND_THRESHOLDS["high"]))
    return {"LOW": low, "MEDIUM": medium, "HIGH": high}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    args = parser.parse_args()
    report = evaluate_risk_engine(args.dataset)
    print(json.dumps(report["test"]["Full Risk Engine"], indent=2))


if __name__ == "__main__":
    main()
