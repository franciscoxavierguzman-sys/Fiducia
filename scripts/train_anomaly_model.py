from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from ml.config import CATEGORICAL_FEATURES, DATASET_PATH, NUMERIC_FEATURES, TARGET
from ml.training.train import dataset_hash, stratified_split

ANOMALY_VERSION = "anomaly-model-v1"
ANOMALY_FEATURES = [
    "source_amount",
    "amount_vs_user_average",
    "transaction_velocity_24h",
    "transaction_velocity_7d",
    "transactions_last_30d",
    "beneficiary_age_days",
    "country_diversity_30d",
    "failed_transaction_ratio",
    "historical_avg_amount",
    "historical_max_amount",
    "transaction_hour",
    "weekend_flag",
    "new_beneficiary_flag",
    "new_corridor_flag",
    "origin_country",
    "destination_country",
    "source_currency",
    "destination_currency",
    "delivery_method",
    "funding_method",
    "relationship",
]
ANOMALY_NUMERIC_FEATURES = [feature for feature in ANOMALY_FEATURES if feature in NUMERIC_FEATURES]
ANOMALY_CATEGORICAL_FEATURES = [feature for feature in ANOMALY_FEATURES if feature in CATEGORICAL_FEATURES]


def train_anomaly_model(dataset_path: Path = DATASET_PATH, artifact_dir: Path = PROJECT_ROOT / "ml" / "artifacts", seed: int = 42) -> dict:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_dir = PROJECT_ROOT / "reports" / "risk_engine"
    report_dir.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(dataset_path)
    missing = [feature for feature in ANOMALY_FEATURES + [TARGET] if feature not in data.columns]
    if missing:
        raise ValueError(f"Dataset incompleto para anomaly detection. Faltan columnas: {missing}")

    x_train, x_validation, x_test, y_train, y_validation, y_test = stratified_split(data, seed)
    preprocessor = ColumnTransformer(
        [
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), ANOMALY_NUMERIC_FEATURES),
            (
                "categorical",
                Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]),
                ANOMALY_CATEGORICAL_FEATURES,
            ),
        ]
    )
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", IsolationForest(n_estimators=160, contamination=0.04, random_state=seed, n_jobs=-1)),
        ]
    )
    pipeline.fit(x_train[ANOMALY_FEATURES])
    train_decision = pipeline.decision_function(x_train[ANOMALY_FEATURES])
    lower = float(np.percentile(train_decision, 1))
    upper = float(np.percentile(train_decision, 99))

    validation_scores = transform_scores(pipeline.decision_function(x_validation[ANOMALY_FEATURES]), lower, upper)
    test_scores = transform_scores(pipeline.decision_function(x_test[ANOMALY_FEATURES]), lower, upper)
    metadata = {
        "algorithm": "IsolationForest",
        "version": ANOMALY_VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "features": ANOMALY_FEATURES,
        "excluded_from_training": [TARGET, "ml_probability", "rule_score", "final_risk_score"],
        "dataset": str(dataset_path),
        "dataset_hash": dataset_hash(dataset_path),
        "seed": seed,
        "normalization_method": "score = clip((p99_train_decision - decision_score) / (p99 - p1) * 100, 0, 100)",
        "calibration": {"lower_decision_score": lower, "upper_decision_score": upper},
        "parameters": {"n_estimators": 160, "contamination": 0.04, "random_state": seed},
        "split": {"train": len(x_train), "validation": len(x_validation), "test": len(x_test), "strategy": "stratified 70/15/15"},
        "evaluation_note": "fraud_label se usa solo para evaluacion posterior, no para entrenamiento.",
        "validation": score_summary(validation_scores, y_validation),
        "test": score_summary(test_scores, y_test),
    }
    artifact = {
        "pipeline": pipeline,
        "features": ANOMALY_FEATURES,
        "numeric_features": ANOMALY_NUMERIC_FEATURES,
        "categorical_features": ANOMALY_CATEGORICAL_FEATURES,
        "model_version": ANOMALY_VERSION,
        "algorithm": "IsolationForest",
        "calibration": metadata["calibration"],
    }
    joblib.dump(artifact, artifact_dir / "anomaly_model.joblib")
    (artifact_dir / "anomaly_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "anomaly_evaluation.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata


def transform_scores(decision_scores, lower: float, upper: float):
    if upper <= lower:
        return np.full_like(decision_scores, 50, dtype=float)
    return np.clip((upper - decision_scores) / (upper - lower) * 100, 0, 100)


def score_summary(scores, labels) -> dict:
    labels = np.asarray(labels)
    return {
        "percentiles": {str(percentile): float(np.percentile(scores, percentile)) for percentile in [1, 5, 25, 50, 75, 95, 99]},
        "normal_mean_score": float(np.mean(scores[labels == 0])),
        "fraud_label_mean_score": float(np.mean(scores[labels == 1])),
        "roc_auc_against_fraud_label": float(roc_auc_score(labels, scores)),
        "pr_auc_against_fraud_label": float(average_precision_score(labels, scores)),
        "extreme_examples_threshold_p95": float(np.percentile(scores, 95)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    args = parser.parse_args()
    metadata = train_anomaly_model(args.dataset, seed=args.seed)
    print(json.dumps({"version": metadata["version"], "features": len(metadata["features"]), "test": metadata["test"]}, indent=2))


if __name__ == "__main__":
    main()
