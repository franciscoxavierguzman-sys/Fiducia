from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.config import (
    ARTIFACT_DIR,
    CATEGORICAL_FEATURES,
    DATASET_PATH,
    EXCLUDED_FEATURES,
    FEATURES,
    MODEL_NAME,
    MODEL_VERSION,
    NUMERIC_FEATURES,
    REPORT_DIR,
    TARGET,
)
from ml.evaluation.metrics import Timer, evaluate_probabilities, find_threshold


def train_fraud_model(
    dataset_path: Path = DATASET_PATH,
    artifact_dir: Path = ARTIFACT_DIR,
    report_dir: Path = REPORT_DIR,
    seed: int = 42,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    data = load_dataset(dataset_path)
    leakage_report = audit_feature_leakage(data)
    x_train, x_validation, x_test, y_train, y_validation, y_test = stratified_split(data, seed)
    models = build_models(seed)

    comparisons: list[dict[str, object]] = []
    fitted_models = {}
    selected_name = ""
    selected_score = (-1.0, -1.0, -1.0)

    for name, pipeline in models.items():
        with Timer() as timer:
            pipeline.fit(x_train, y_train)
        probabilities_validation = _predict_probability(pipeline, x_validation)
        threshold_info = find_threshold(y_validation, probabilities_validation)
        validation_metrics = evaluate_probabilities(y_validation, probabilities_validation, threshold_info["threshold"])
        probabilities_test = _predict_probability(pipeline, x_test)
        test_metrics = evaluate_probabilities(y_test, probabilities_test, threshold_info["threshold"])
        row = {
            "model": name,
            "algorithm": pipeline.named_steps["model"].__class__.__name__,
            "training_time_seconds": round(timer.elapsed_seconds, 4),
            "threshold": threshold_info["threshold"],
            "validation": validation_metrics,
            "test": test_metrics,
        }
        comparisons.append(row)
        fitted_models[name] = pipeline
        score = (float(validation_metrics["pr_auc"]), float(validation_metrics["recall"]), float(validation_metrics["precision"]))
        if name != "Dummy" and score > selected_score:
            selected_score = score
            selected_name = name

    selected_pipeline = fitted_models[selected_name]
    selected = next(item for item in comparisons if item["model"] == selected_name)
    feature_importance = extract_feature_importance(selected_pipeline, x_validation, y_validation, seed=seed)
    artifact_path = artifact_dir / "fraud_model.joblib"
    metadata_path = artifact_dir / "model_metadata.json"
    metrics_path = artifact_dir / "model_metrics.json"

    artifact = {
        "pipeline": selected_pipeline,
        "features": FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "threshold": selected["threshold"],
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }
    joblib.dump(artifact, artifact_path)

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "algorithm": selected["algorithm"],
        "selected_model": selected_name,
        "features": FEATURES,
        "excluded_features": EXCLUDED_FEATURES,
        "threshold": selected["threshold"],
        "dataset": str(dataset_path),
        "dataset_hash": dataset_hash(dataset_path),
        "seed": seed,
        "class_distribution": data[TARGET].value_counts().sort_index().astype(int).to_dict(),
        "split": {"train": len(y_train), "validation": len(y_validation), "test": len(y_test), "strategy": "stratified 70/15/15"},
        "metrics": selected["test"],
        "limitations": [
            "Entrenado con datos sinteticos.",
            "No confirma fraude real.",
            "No debe bloquear remesas automaticamente.",
        ],
    }
    metrics = {"comparison": comparisons, "selected_model": selected_name, "feature_importance": feature_importance}
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "model_comparison.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "artifact_path": str(artifact_path),
        "metadata_path": str(metadata_path),
        "metrics_path": str(metrics_path),
        "metadata": metadata,
        "metrics": metrics,
        "leakage_report": leakage_report,
    }


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    data = pd.read_csv(dataset_path)
    missing = [feature for feature in FEATURES + [TARGET] if feature not in data.columns]
    if missing:
        raise ValueError(f"Dataset incompleto. Faltan columnas: {missing}")
    return data


def audit_feature_leakage(data: pd.DataFrame) -> dict[str, object]:
    included_overlap = sorted(set(FEATURES).intersection(EXCLUDED_FEATURES + [TARGET]))
    missing_excluded = [feature for feature in EXCLUDED_FEATURES if feature not in data.columns]
    return {
        "valid": not included_overlap,
        "included_overlap": included_overlap,
        "excluded_features_present_but_not_used": [feature for feature in EXCLUDED_FEATURES if feature in data.columns],
        "excluded_features_missing": missing_excluded,
    }


def stratified_split(data: pd.DataFrame, seed: int):
    x = data[FEATURES]
    y = data[TARGET].astype(int)
    x_train, x_temp, y_train, y_temp = train_test_split(x, y, test_size=0.30, random_state=seed, stratify=y)
    x_validation, x_test, y_validation, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=0.50,
        random_state=seed,
        stratify=y_temp,
    )
    return x_train, x_validation, x_test, y_train, y_validation, y_test


def build_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(numeric_steps)
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def build_models(seed: int) -> dict[str, Pipeline]:
    return {
        "Dummy": Pipeline([("preprocessor", build_preprocessor()), ("model", DummyClassifier(strategy="prior"))]),
        "Logistic Regression": Pipeline(
            [
                ("preprocessor", build_preprocessor(scale_numeric=True)),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed)),
            ]
        ),
        "Random Forest": Pipeline(
            [
                ("preprocessor", build_preprocessor(scale_numeric=False)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=8,
                        min_samples_leaf=8,
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "Gradient Boosting": Pipeline(
            [
                ("preprocessor", build_preprocessor(scale_numeric=False)),
                ("model", HistGradientBoostingClassifier(max_iter=120, learning_rate=0.06, max_leaf_nodes=24, random_state=seed)),
            ]
        ),
    }


def extract_feature_importance(pipeline: Pipeline, x_validation=None, y_validation=None, seed: int = 42, limit: int = 20) -> list[dict[str, object]]:
    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = FEATURES
    values = None
    if hasattr(model, "coef_"):
        values = model.coef_[0]
    elif hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    if values is None:
        if x_validation is None or y_validation is None:
            return []
        importance = permutation_importance(
            pipeline,
            x_validation,
            y_validation,
            n_repeats=5,
            random_state=seed,
            scoring="average_precision",
        )
        pairs = sorted(zip(FEATURES, importance.importances_mean), key=lambda item: abs(float(item[1])), reverse=True)
        return [{"feature": str(feature), "importance": float(value), "method": "permutation_importance"} for feature, value in pairs[:limit]]
    pairs = sorted(zip(feature_names, values), key=lambda item: abs(float(item[1])), reverse=True)
    return [{"feature": str(feature), "importance": float(value), "method": "native_or_coefficient"} for feature, value in pairs[:limit]]


def dataset_hash(dataset_path: Path) -> str:
    digest = hashlib.sha256()
    with dataset_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _predict_probability(pipeline: Pipeline, features):
    model = pipeline.named_steps["model"]
    if hasattr(model, "predict_proba"):
        return pipeline.predict_proba(features)[:, 1]
    return pipeline.predict(features)
