from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import HTTPException, status

from app.schemas.ml_risk import MLModelInfo, MLPredictResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_PATH = PROJECT_ROOT / "ml" / "artifacts" / "fraud_model.joblib"
METADATA_PATH = PROJECT_ROOT / "ml" / "artifacts" / "model_metadata.json"
METRICS_PATH = PROJECT_ROOT / "ml" / "artifacts" / "model_metrics.json"


def get_model_info() -> MLModelInfo:
    if not ARTIFACT_PATH.exists() or not METADATA_PATH.exists():
        return MLModelInfo(available=False, message="Modelo ML no entrenado o artefacto no disponible.")
    metadata = _load_metadata()
    return MLModelInfo(
        available=True,
        model_name=metadata.get("model_name"),
        model_version=metadata.get("model_version"),
        algorithm=metadata.get("algorithm"),
        selected_model=metadata.get("selected_model"),
        trained_at=metadata.get("trained_at"),
        threshold=metadata.get("threshold"),
        features=metadata.get("features", []),
        dataset_hash=metadata.get("dataset_hash"),
    )


def get_model_metrics() -> dict[str, Any]:
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "ML_METRICS_NOT_AVAILABLE", "message": "Metricas del modelo no disponibles"},
        )
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def predict_fraud_probability(features: dict[str, Any]) -> MLPredictResponse:
    artifact = _load_model_artifact()
    expected_features = artifact.get("features", [])
    missing = [feature for feature in expected_features if feature not in features]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "ML_FEATURES_MISSING", "message": "Faltan features requeridas", "missing_features": missing},
        )

    row = {feature: features[feature] for feature in expected_features}
    frame = pd.DataFrame([row])
    try:
        probability = float(artifact["pipeline"].predict_proba(frame)[0][1])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ML_INFERENCE_FAILED", "message": "No se pudo ejecutar inferencia ML"},
        ) from exc
    threshold = float(artifact["threshold"])
    classification = _classification(probability, threshold)
    return MLPredictResponse(
        ml_probability=probability,
        model_version=artifact["model_version"],
        threshold=threshold,
        classification=classification,
        classification_label={"LOW": "Bajo", "MEDIUM": "Medio", "HIGH": "Alto"}[classification],
        top_features=_top_features(),
    )


@lru_cache(maxsize=1)
def _load_model_artifact() -> dict[str, Any]:
    if not ARTIFACT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "ML_MODEL_NOT_AVAILABLE", "message": "Modelo ML no entrenado o artefacto no disponible"},
        )
    try:
        return joblib.load(ARTIFACT_PATH)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "ML_MODEL_LOAD_FAILED", "message": "No se pudo cargar el modelo ML"},
        ) from exc


def _load_metadata() -> dict[str, Any]:
    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _top_features() -> list[dict[str, Any]]:
    if not METRICS_PATH.exists():
        return []
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return metrics.get("feature_importance", [])[:8]


def _classification(probability: float, threshold: float) -> str:
    if probability >= threshold:
        return "HIGH"
    if probability >= threshold / 2:
        return "MEDIUM"
    return "LOW"

