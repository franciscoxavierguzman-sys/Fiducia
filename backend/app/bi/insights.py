from __future__ import annotations

from decimal import Decimal


def build_executive_insights(overview_comparison: dict, corridors: list[dict], operations: dict, risk: dict, forecast: dict) -> list[dict]:
    insights = []
    changes = overview_comparison.get("changes", {})
    current = overview_comparison.get("current", {})
    volume_change = changes.get("total_remittances", {}).get("percentage_change")
    revenue_change = changes.get("total_commission_revenue_usd_equivalent", {}).get("percentage_change")
    ticket_change = changes.get("average_ticket_usd_equivalent", {}).get("percentage_change")
    if volume_change is not None:
        insights.append(_movement_insight("total_remittances", "volumen", Decimal(str(volume_change))))
    if revenue_change is not None:
        insights.append(_movement_insight("total_commission_revenue_usd_equivalent", "ingresos por comision", Decimal(str(revenue_change))))
    if ticket_change is not None:
        insights.append(_movement_insight("average_ticket_usd_equivalent", "ticket promedio", Decimal(str(ticket_change))))
    if corridors:
        top = corridors[0]
        insights.append(
            {
                "priority": "INFO",
                "code": "top_corridor",
                "message": f"El corredor con mayor revenue es {top['corridor']} con {top['remittance_count']} remesas.",
                "source_kpis": ["commission_revenue_by_corridor", "remittance_count"],
            }
        )
    high_share = next((item["share"] for item in risk.get("risk_distribution", []) if item["risk_band"] == "HIGH"), None)
    if high_share is not None and Decimal(str(high_share)) >= Decimal("0.10"):
        insights.append(
            {
                "priority": "ATTENTION",
                "code": "high_risk_share",
                "message": f"Las operaciones en banda alta representan {Decimal(str(high_share)) * 100:.2f}% de assessments agregados.",
                "source_kpis": ["risk_distribution"],
            }
        )
    if operations.get("review_required", 0) > 0:
        insights.append(
            {
                "priority": "ATTENTION",
                "code": "review_queue",
                "message": f"Hay {operations['review_required']} remesas con revision requerida en el periodo.",
                "source_kpis": ["review_required"],
            }
        )
    if forecast:
        insights.append(
            {
                "priority": "INFO",
                "code": "forecast_status",
                "message": f"Forecast ejecutivo disponible en estado {forecast.get('go_decision', 'CONDITIONAL')} para las proximas 4 semanas.",
                "source_kpis": ["forecast_outlook"],
            }
        )
    if not insights:
        insights.append({"priority": "INFO", "code": "stable_period", "message": "No se detectaron variaciones relevantes con los filtros actuales.", "source_kpis": list(current)})
    return insights


def _movement_insight(code: str, label: str, change: Decimal) -> dict:
    direction = "aumento" if change > 0 else "disminuyo" if change < 0 else "se mantuvo estable"
    priority = "ATTENTION" if abs(change) >= Decimal("0.20") else "INFO"
    return {
        "priority": priority,
        "code": f"{code}_change",
        "message": f"El {label} {direction} {abs(change) * 100:.2f}% frente al periodo anterior.",
        "source_kpis": [code],
    }
