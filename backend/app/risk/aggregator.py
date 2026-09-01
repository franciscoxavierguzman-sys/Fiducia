from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RISK_ENGINE_VERSION = "risk-engine-v1.1"
AGGREGATION_STRATEGY = "weighted_available_signals_v1"
RISK_ENGINE_WEIGHTS = {"rules": 0.30, "ml": 0.50, "anomaly": 0.20}
RISK_BAND_THRESHOLDS = {"medium": 25.0, "high": 40.0}


@dataclass(frozen=True)
class AggregatedRisk:
    final_risk_score: float | None
    risk_band: str
    recommended_action: str
    weights_used: dict[str, float]
    signal_status: dict[str, str]
    explanations: list[str]


def aggregate_risk(rule_score: float | None, ml_probability: float | None, anomaly_score: float | None) -> AggregatedRisk:
    signals = {
        "rules": rule_score,
        "ml": ml_probability * 100 if ml_probability is not None else None,
        "anomaly": anomaly_score,
    }
    available = {name: value for name, value in signals.items() if value is not None}
    signal_status = {name: "available" if value is not None else "unavailable" for name, value in signals.items()}
    if not available:
        return AggregatedRisk(None, "UNKNOWN", "REVIEW", {}, signal_status, ["No hay senales disponibles para calcular riesgo."])

    available_weight = sum(RISK_ENGINE_WEIGHTS[name] for name in available)
    weights_used = {name: RISK_ENGINE_WEIGHTS[name] / available_weight for name in available}
    score = sum(float(available[name]) * weights_used[name] for name in available)
    score = max(0.0, min(100.0, score))
    band = assign_risk_band(score)
    action = recommended_action_for_band(band)
    explanations = [
        f"Score combinado calculado con estrategia {AGGREGATION_STRATEGY}.",
        f"Senales disponibles: {', '.join(sorted(available))}.",
    ]
    if any(value == "unavailable" for value in signal_status.values()):
        explanations.append("La evaluacion se genero en modo degradado porque una o mas senales no estaban disponibles.")
    return AggregatedRisk(round(score, 2), band, action, weights_used, signal_status, explanations)


def assign_risk_band(score: float) -> str:
    if score >= RISK_BAND_THRESHOLDS["high"]:
        return "HIGH"
    if score >= RISK_BAND_THRESHOLDS["medium"]:
        return "MEDIUM"
    return "LOW"


def recommended_action_for_band(band: str) -> str:
    if band == "HIGH":
        return "MANUAL_REVIEW"
    if band == "MEDIUM":
        return "REVIEW"
    return "CONTINUE"


def engine_metadata() -> dict[str, Any]:
    return {
        "version": RISK_ENGINE_VERSION,
        "aggregation_strategy": AGGREGATION_STRATEGY,
        "weights": RISK_ENGINE_WEIGHTS,
        "risk_band_thresholds": RISK_BAND_THRESHOLDS,
        "recommended_actions": {"LOW": "CONTINUE", "MEDIUM": "REVIEW", "HIGH": "MANUAL_REVIEW"},
        "weights_status": "baseline heuristico inicial",
        "bands_status": "thresholds operativos de Decision Support",
    }
