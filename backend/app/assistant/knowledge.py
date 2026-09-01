from __future__ import annotations

import re
from datetime import date


KNOWLEDGE_BASE = [
    {
        "id": "support-beneficiaries",
        "title": "Beneficiarios",
        "content": "Para agregar un beneficiario abre Beneficiarios, completa datos, pais, moneda y metodo de entrega. Si el beneficiario tambien tiene cuenta FIDUCIA, usa el mismo correo para vincular remesas recibidas.",
        "source": "FIDUCIA help",
        "version": "assistant-kb-v1",
        "allowed_roles": ["CLIENT", "RISK_ANALYST", "ADMIN"],
        "updated_at": date(2026, 9, 1).isoformat(),
    },
    {
        "id": "support-status-available",
        "title": "Estado Disponible",
        "content": "Disponible significa que la remesa ya fue creada y esta lista para recepcion o cobro segun el metodo de entrega configurado. No significa que haya sido recibida.",
        "source": "FIDUCIA help",
        "version": "assistant-kb-v1",
        "allowed_roles": ["CLIENT", "RISK_ANALYST", "ADMIN"],
        "updated_at": date(2026, 9, 1).isoformat(),
    },
    {
        "id": "support-fees",
        "title": "Comisiones",
        "content": "La comision se calcula en backend durante la cotizacion y se conserva en la remesa. El frontend no recalcula la comision como fuente de verdad.",
        "source": "FIDUCIA help",
        "version": "assistant-kb-v1",
        "allowed_roles": ["CLIENT", "RISK_ANALYST", "ADMIN"],
        "updated_at": date(2026, 9, 1).isoformat(),
    },
    {
        "id": "support-risk",
        "title": "Riesgo",
        "content": "El motor de riesgo combina reglas, probabilidad ML y anomalias para apoyar revision humana. No confirma fraude ni bloquea automaticamente una remesa.",
        "source": "FIDUCIA help",
        "version": "assistant-kb-v1",
        "allowed_roles": ["RISK_ANALYST", "ADMIN"],
        "updated_at": date(2026, 9, 1).isoformat(),
    },
    {
        "id": "support-blockchain",
        "title": "Blockchain",
        "content": "La blockchain local registra hashes de evidencia para detectar alteraciones posteriores. Verifica integridad de evidencia, no legitimidad financiera de una operacion.",
        "source": "FIDUCIA help",
        "version": "assistant-kb-v1",
        "allowed_roles": ["CLIENT", "RISK_ANALYST", "ADMIN"],
        "updated_at": date(2026, 9, 1).isoformat(),
    },
]


def search_knowledge(query: str, role: str) -> dict:
    tokens = {token for token in re.findall(r"[a-záéíóúñ0-9]+", query.lower()) if len(token) >= 4}
    allowed = [item for item in KNOWLEDGE_BASE if role in item["allowed_roles"]]
    scored = []
    for item in allowed:
        haystack = f"{item['title']} {item['content']}".lower()
        score = sum(1 for token in tokens if token in haystack)
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    selected = scored[0][1] if scored else allowed[0]
    return selected
