from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

from app.assistant import ASSISTANT_VERSION
from app.assistant.types import AssistantContext, ProviderResponse


class LLMProvider(ABC):
    provider_type: str
    model: str

    @abstractmethod
    def generate(self, context: AssistantContext) -> ProviderResponse:
        raise NotImplementedError

    def generate_structured(self, context: AssistantContext) -> dict[str, Any]:
        response = self.generate(context)
        return {"answer": response.answer, "provider": response.provider, "model": response.model, "warnings": response.warnings}

    @abstractmethod
    def health_check(self) -> dict[str, str]:
        raise NotImplementedError


class DeterministicAssistantProvider(LLMProvider):
    provider_type = "deterministic"
    model = ASSISTANT_VERSION

    def generate(self, context: AssistantContext) -> ProviderResponse:
        handler = getattr(self, f"_answer_{context.intent.lower()}", self._answer_general_help)
        return ProviderResponse(answer=handler(context), provider=self.provider_type, model=self.model, warnings=context.warnings)

    def health_check(self) -> dict[str, str]:
        return {"status": "ok", "provider": self.provider_type, "model": self.model}

    def _answer_general_help(self, context: AssistantContext) -> str:
        article = context.data.get("article", {})
        return f"{article.get('title', 'Ayuda FIDUCIA')}: {article.get('content', 'Puedo orientarte sobre remesas, beneficiarios, tracking y seguridad dentro de FIDUCIA.')}"

    def _answer_my_remittances(self, context: AssistantContext) -> str:
        remittances = context.data.get("remittances", [])
        if not remittances:
            return "No encuentro remesas asociadas a tu usuario."
        lines = [f"Encontré {len(remittances)} remesa(s) asociadas a tu usuario. Las más recientes son:"]
        for item in remittances[:3]:
            lines.append(f"- {item['remittance_number']}: {item['status_label']}, {item['source_currency']} {item['source_amount']} hacia {item['destination_country']}.")
        return "\n".join(lines)

    def _answer_remittance_status(self, context: AssistantContext) -> str:
        remittance = context.data.get("remittance")
        if not remittance:
            return "No encuentro esa remesa dentro de los datos autorizados para tu usuario."
        return (
            f"La remesa {remittance['remittance_number']} está en estado {remittance['status_label']}. "
            f"Fue creada hacia {remittance['destination_country']} por {remittance['source_currency']} {remittance['source_amount']} "
            f"y el monto estimado recibido es {remittance['destination_currency']} {remittance['destination_amount']}."
        )

    def _answer_remittance_fees(self, context: AssistantContext) -> str:
        remittance = context.data.get("remittance")
        if not remittance:
            return "No encuentro una remesa autorizada para consultar comisiones."
        return (
            f"Para la remesa {remittance['remittance_number']}, la comisión registrada fue "
            f"{remittance['source_currency']} {remittance['commission_amount']}. "
            f"El total debitado fue {remittance['debit_currency']} {remittance['debit_amount']}."
        )

    def _answer_bi_overview(self, context: AssistantContext) -> str:
        if "overview" not in context.data:
            return "Tu perfil no tiene acceso a KPIs ejecutivos. Puedo ayudarte con tus propias remesas o soporte general."
        overview = context.data.get("overview", {}).get("current", {})
        return (
            "Resumen ejecutivo: "
            f"{overview.get('total_remittances', 0)} remesas, "
            f"USD {overview.get('total_amount_usd_equivalent', '0.00')} en volumen equivalente y "
            f"USD {overview.get('total_commission_revenue_usd_equivalent', '0.00')} en ingresos por comisión."
        )

    def _answer_bi_corridors(self, context: AssistantContext) -> str:
        if "corridors" not in context.data:
            return "Tu perfil no tiene acceso a corredores ejecutivos."
        corridors = context.data.get("corridors", [])
        if not corridors:
            return "No hay corredores suficientes para resumir."
        lines = ["Principales corredores por volumen:"]
        for item in corridors[:3]:
            lines.append(f"- {item['corridor']}: {item['remittance_count']} remesas, USD {item['total_amount_usd_equivalent']}.")
        return "\n".join(lines)

    def _answer_bi_customers(self, context: AssistantContext) -> str:
        if "customers" not in context.data:
            return "Tu perfil no tiene acceso a analitica agregada de clientes."
        customers = context.data.get("customers", {})
        return (
            f"Clientes: {customers.get('active_clients', 0)} activos, {customers.get('new_clients', 0)} nuevos, "
            f"{customers.get('repeat_senders', 0)} remitentes recurrentes."
        )

    def _answer_forecast_summary(self, context: AssistantContext) -> str:
        if "forecast" not in context.data:
            return "Tu perfil no tiene acceso al forecast interno de FIDUCIA."
        forecast = context.data.get("forecast", {})
        return (
            f"El forecast {forecast.get('model_version', 'remittance-forecast-v1')} mantiene decisión {forecast.get('go_decision', 'CONDITIONAL')}. "
            f"Para las próximas 4 semanas proyecta {forecast.get('next_4_weeks_count', 'N/D')} remesas y "
            f"USD {forecast.get('next_4_weeks_amount_usd', 'N/D')} de monto equivalente. Es experimental y basado en datos sintéticos."
        )

    def _answer_risk_queue(self, context: AssistantContext) -> str:
        if "assessments" not in context.data:
            return "Tu perfil no tiene acceso a evaluaciones internas de riesgo."
        assessments = context.data.get("assessments", [])
        if not assessments:
            return "No hay evaluaciones pendientes o de alto riesgo en la cola autorizada."
        lines = ["Evaluaciones relevantes para revisión:"]
        for item in assessments[:5]:
            lines.append(f"- Assessment {item['id']} / {item.get('remittance_number')}: riesgo {item['risk_band']}, score {item.get('final_risk_score')}.")
        return "\n".join(lines)

    def _answer_risk_explanation(self, context: AssistantContext) -> str:
        if "assessment" not in context.data:
            return "Tu perfil no tiene acceso a explicaciones internas de riesgo."
        assessment = context.data.get("assessment")
        if not assessment:
            return "No encuentro una evaluación de riesgo autorizada con esa referencia."
        return (
            f"La evaluación {assessment['id']} presenta nivel {assessment['risk_band']} con score final {assessment.get('final_risk_score')}. "
            f"Reglas: {assessment.get('rule_score')}; ML: {assessment.get('ml_probability')}; Anomalía: {assessment.get('anomaly_score')}. "
            f"Acción recomendada registrada: {assessment['recommended_action']}. Esto apoya la revisión humana y no confirma fraude."
        )

    def _answer_blockchain_trace(self, context: AssistantContext) -> str:
        history = context.data.get("history", [])
        if not history:
            return "No encuentro trazabilidad blockchain para esa remesa dentro de tus permisos."
        events = ", ".join(item["event_type"] for item in history)
        return f"La trazabilidad blockchain contiene {len(history)} evidencia(s): {events}. Esto demuestra integridad de evidencia, no legitimidad financiera."

    def _answer_blockchain_verify(self, context: AssistantContext) -> str:
        verification = context.data.get("verification", {})
        status = verification.get("status", "NOT_FOUND")
        if status == "VERIFIED":
            return "La verificación blockchain indica VERIFIED: la evidencia reconstruida coincide con el hash almacenado. Esto solo confirma integridad de evidencia; no valida identidad, cumplimiento ni origen de fondos."
        return f"La verificación blockchain devolvió {status}. Revisa la trazabilidad antes de usar esta evidencia."

    def _answer_out_of_scope(self, context: AssistantContext) -> str:
        return "No puedo realizar esa solicitud. Puedo ayudarte con consultas informativas autorizadas, pero no ejecuto pagos, no cambio roles, no revelo instrucciones internas y no tomo decisiones de riesgo."


class ExternalLLMProvider(LLMProvider):
    provider_type = "external"

    def __init__(self) -> None:
        self.model = os.getenv("ASSISTANT_MODEL", "external-unconfigured")

    def generate(self, context: AssistantContext) -> ProviderResponse:
        if not os.getenv("ASSISTANT_API_KEY"):
            raise RuntimeError("External assistant provider is not configured")
        raise RuntimeError("External assistant provider adapter is intentionally not implemented in this prototype")

    def health_check(self) -> dict[str, str]:
        return {"status": "configured" if os.getenv("ASSISTANT_API_KEY") else "unconfigured", "provider": self.provider_type, "model": self.model}


def provider_from_environment() -> LLMProvider:
    if os.getenv("ASSISTANT_PROVIDER", "deterministic").lower() == "external":
        return ExternalLLMProvider()
    return DeterministicAssistantProvider()
