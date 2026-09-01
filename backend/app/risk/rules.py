from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RULES_VERSION = "rules-v1"


@dataclass(frozen=True)
class RiskRule:
    rule_id: str
    rule_code: str
    name: str
    description: str
    severity: str
    score_contribution: int
    enabled: bool
    version: str


RULE_CATALOG = [
    RiskRule("1", "R001", "Monto inusual", "Monto mayor a 3 veces el promedio historico del usuario.", "HIGH", 18, True, "1.0"),
    RiskRule("2", "R002", "Alta velocidad 24h", "Tres o mas remesas previas en las ultimas 24 horas.", "HIGH", 18, True, "1.0"),
    RiskRule("3", "R003", "Alta velocidad 7d", "Cinco o mas remesas previas en los ultimos 7 dias.", "MEDIUM", 12, True, "1.0"),
    RiskRule("4", "R004", "Beneficiario nuevo", "Beneficiario sin historial o creado hace siete dias o menos.", "MEDIUM", 10, True, "1.0"),
    RiskRule("5", "R005", "Corredor nuevo", "Primer uso observado del corredor por el remitente.", "MEDIUM", 10, True, "1.0"),
    RiskRule("6", "R006", "Horario atipico", "Operacion creada entre medianoche y 5:59.", "LOW", 6, True, "1.0"),
    RiskRule("7", "R007", "Incremento abrupto", "Monto mayor a 2 veces el maximo historico previo.", "HIGH", 16, True, "1.0"),
    RiskRule("8", "R008", "Diversidad reciente", "Tres o mas paises destino usados en los ultimos 30 dias.", "MEDIUM", 10, True, "1.0"),
    RiskRule("9", "R009", "Fallas previas", "Ratio de fallas historicas igual o superior a 25%.", "MEDIUM", 10, True, "1.0"),
    RiskRule("10", "R010", "Combinacion conductual", "Beneficiario nuevo con monto alto y velocidad reciente.", "HIGH", 16, True, "1.0"),
]


def evaluate_rules(features: dict[str, Any]) -> dict[str, Any]:
    triggered = []
    for rule in RULE_CATALOG:
        if not rule.enabled:
            continue
        reason = _evaluate_rule(rule.rule_code, features)
        if reason:
            triggered.append(
                {
                    "rule_id": rule.rule_id,
                    "rule_code": rule.rule_code,
                    "name": rule.name,
                    "description": rule.description,
                    "severity": rule.severity,
                    "contribution": rule.score_contribution,
                    "reason": reason,
                    "version": rule.version,
                }
            )
    raw_score = sum(item["contribution"] for item in triggered)
    return {
        "rule_score": min(100, raw_score),
        "raw_rule_score": raw_score,
        "triggered_rules": triggered,
        "rules_version": RULES_VERSION,
        "available": True,
    }


def _evaluate_rule(code: str, features: dict[str, Any]) -> str | None:
    amount = float(features.get("source_amount") or 0)
    avg = float(features.get("historical_avg_amount") or 0)
    max_amount = float(features.get("historical_max_amount") or 0)
    velocity_24h = int(features.get("transaction_velocity_24h") or 0)
    velocity_7d = int(features.get("transaction_velocity_7d") or 0)
    new_beneficiary = int(features.get("new_beneficiary_flag") or 0)
    new_corridor = int(features.get("new_corridor_flag") or 0)
    unusual_hour = int(features.get("unusual_hour_flag") or 0)
    country_diversity = int(features.get("country_diversity_30d") or 0)
    failed_ratio = float(features.get("failed_transaction_ratio") or 0)
    amount_vs_average = float(features.get("amount_vs_user_average") or 1)

    if code == "R001" and avg > 0 and amount_vs_average >= 3:
        return f"Monto {amount:.2f} equivale a {amount_vs_average:.2f} veces el promedio historico."
    if code == "R002" and velocity_24h >= 3:
        return f"{velocity_24h} remesas previas en 24 horas."
    if code == "R003" and velocity_7d >= 5:
        return f"{velocity_7d} remesas previas en 7 dias."
    if code == "R004" and new_beneficiary:
        return "Beneficiario nuevo o sin historial previo."
    if code == "R005" and new_corridor:
        return "Corredor sin uso previo por el remitente."
    if code == "R006" and unusual_hour:
        return "Operacion creada en horario de baja actividad."
    if code == "R007" and max_amount > 0 and amount >= max_amount * 2:
        return f"Monto {amount:.2f} supera dos veces el maximo historico {max_amount:.2f}."
    if code == "R008" and country_diversity >= 3:
        return f"{country_diversity} paises destino utilizados en los ultimos 30 dias."
    if code == "R009" and failed_ratio >= 0.25:
        return f"Ratio de fallas historicas {failed_ratio:.2%}."
    if code == "R010" and new_beneficiary and velocity_24h >= 1 and (amount_vs_average >= 2.5 or amount >= 1000):
        return "Beneficiario nuevo combinado con monto alto y actividad reciente."
    return None
