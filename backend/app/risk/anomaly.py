from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ANOMALY_ARTIFACT_PATH = PROJECT_ROOT / "ml" / "artifacts" / "anomaly_model.joblib"
ANOMALY_METADATA_PATH = PROJECT_ROOT / "ml" / "artifacts" / "anomaly_metadata.json"


def predict_anomaly_score(features: dict[str, Any]) -> dict[str, Any]:
    artifact = _load_anomaly_artifact()
    expected = artifact["features"]
    missing = [feature for feature in expected if feature not in features]
    if missing:
        raise ValueError(f"Faltan features de anomalia: {missing}")
    frame = pd.DataFrame([{feature: features[feature] for feature in expected}])
    decision_score = float(artifact["pipeline"].decision_function(frame)[0])
    lower = float(artifact["calibration"]["lower_decision_score"])
    upper = float(artifact["calibration"]["upper_decision_score"])
    if upper <= lower:
        anomaly_score = 50.0
    else:
        anomaly_score = (upper - decision_score) / (upper - lower) * 100
    anomaly_score = float(np.clip(anomaly_score, 0, 100))
    return {
        "available": True,
        "anomaly_score": round(anomaly_score, 2),
        "raw_decision_score": decision_score,
        "model_version": artifact["model_version"],
        "algorithm": artifact["algorithm"],
    }


def anomaly_model_info() -> dict[str, Any]:
    if not ANOMALY_ARTIFACT_PATH.exists() or not ANOMALY_METADATA_PATH.exists():
        return {"available": False, "message": "Detector de anomalias no entrenado."}
    try:
        metadata = json.loads(ANOMALY_METADATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        metadata = {}
    return {"available": True, **metadata}


@lru_cache(maxsize=1)
def _load_anomaly_artifact() -> dict[str, Any]:
    if not ANOMALY_ARTIFACT_PATH.exists():
        raise FileNotFoundError("anomaly_model.joblib no disponible")
    return joblib.load(ANOMALY_ARTIFACT_PATH)
