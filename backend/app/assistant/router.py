from __future__ import annotations

import re

from app.assistant.types import IntentResult


ROLE_ESCALATION_PATTERNS = [
    r"\bahora soy admin\b",
    r"\bsoy admin\b",
    r"\bactua como admin\b",
    r"\bactúa como admin\b",
    r"\bmi rol es admin\b",
]
PROMPT_INJECTION_PATTERNS = [
    r"\bignora\b.*\binstrucciones\b",
    r"\bignore\b.*\binstructions\b",
    r"\bmu[eé]strame todos los clientes\b",
    r"\brevela\b.*\bprompt\b",
]
SYSTEM_PROMPT_PATTERNS = [
    r"\binstrucciones del sistema\b",
    r"\bsystem prompt\b",
    r"\bprompt interno\b",
]


def route_intent(message: str) -> IntentResult:
    text = _normalize(message)
    safety_events: list[str] = []
    if _matches(text, ROLE_ESCALATION_PATTERNS):
        safety_events.append("ROLE_ESCALATION_ATTEMPT")
        return IntentResult("OUT_OF_SCOPE", 0.98, safety_events)
    if _matches(text, SYSTEM_PROMPT_PATTERNS):
        safety_events.append("SYSTEM_PROMPT_REQUEST")
        return IntentResult("OUT_OF_SCOPE", 0.98, safety_events)
    if _matches(text, PROMPT_INJECTION_PATTERNS):
        safety_events.append("PROMPT_INJECTION_ATTEMPT")
        return IntentResult("OUT_OF_SCOPE", 0.98, safety_events)
    if any(term in text for term in ["rechazala", "recházala", "apruebala", "apruébala", "cancela", "envia ", "envía ", "manda dinero"]):
        return IntentResult("OUT_OF_SCOPE", 0.92, safety_events)
    if any(term in text for term in ["blockchain", "cadena", "hash", "evidencia"]):
        return IntentResult("BLOCKCHAIN_VERIFY" if any(term in text for term in ["verifica", "valid", "coincide"]) else "BLOCKCHAIN_TRACE", 0.87, safety_events)
    if any(term in text for term in ["riesgo", "score", "evaluacion", "evaluación", "senales", "señales", "high"]):
        if any(term in text for term in ["cola", "pendiente", "requieren revision", "mayor riesgo", "high"]):
            return IntentResult("RISK_QUEUE", 0.86, safety_events)
        return IntentResult("RISK_EXPLANATION", 0.84, safety_events)
    if any(term in text for term in ["comision", "comisión", "pague", "pagué"]):
        return IntentResult("REMITTANCE_FEES", 0.87, safety_events)
    if any(term in text for term in ["ultima remesa", "última remesa", "estado", "fid-"]):
        return IntentResult("REMITTANCE_STATUS", 0.87, safety_events)
    if any(term in text for term in ["mis remesas", "historial", "enviadas", "recibidas"]):
        return IntentResult("MY_REMITTANCES", 0.83, safety_events)
    if any(term in text for term in ["forecast", "pronost", "proyecta", "proximo mes", "próximo mes"]):
        return IntentResult("FORECAST_SUMMARY", 0.86, safety_events)
    if any(term in text for term in ["kpi", "volumen", "comision gener", "corredores", "clientes", "desempeno", "desempeño"]) or re.search(r"\bmes\b", text):
        if "corredor" in text or "corredores" in text:
            return IntentResult("BI_CORRIDORS", 0.86, safety_events)
        if "cliente" in text:
            return IntentResult("BI_CUSTOMERS", 0.82, safety_events)
        return IntentResult("BI_OVERVIEW", 0.84, safety_events)
    if any(term in text for term in ["beneficiario", "disponible", "tracking", "rastrear", "ayuda", "como", "cómo", "que significa", "qué significa"]):
        return IntentResult("GENERAL_HELP", 0.80, safety_events)
    return IntentResult("GENERAL_HELP", 0.45, safety_events)


def extract_remittance_number(message: str) -> str | None:
    match = re.search(r"FID-\d{4}-\d{6}", message.upper())
    return match.group(0) if match else None


def extract_integer(message: str) -> int | None:
    match = re.search(r"\b\d+\b", message)
    return int(match.group(0)) if match else None


def _matches(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _normalize(value: str) -> str:
    return value.lower().strip()
