from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.assistant.knowledge import search_knowledge
from app.bi.filters import BIFilters
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transactions import get_transaction_by_number, list_received_transactions, list_sent_transactions
from app.services.blockchain import transaction_history, verify_transaction_evidence
from app.services.business_intelligence import get_bi_corridors, get_bi_customers, get_bi_overview, get_bi_forecast
from app.services.risk_engine import get_assessment_or_404, list_assessments


@dataclass(frozen=True)
class AssistantTool:
    name: str
    description: str
    allowed_roles: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    handler: Callable[[Session, User, dict[str, Any]], dict[str, Any]]


def tool_registry() -> dict[str, AssistantTool]:
    tools = [
        AssistantTool("get_support_article", "Busca ayuda curada de FIDUCIA.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {"query": "string"}, {"article": "object"}, get_support_article),
        AssistantTool("get_my_remittances", "Consulta remesas propias del usuario.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {}, {"remittances": "array"}, get_my_remittances),
        AssistantTool("get_remittance_status", "Consulta estado de una remesa autorizada.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {"remittance_number": "string?"}, {"remittance": "object|null"}, get_remittance_status),
        AssistantTool("get_remittance_fee", "Consulta comision de una remesa autorizada.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {"remittance_number": "string?"}, {"remittance": "object|null"}, get_remittance_fee),
        AssistantTool("get_bi_overview", "Consulta KPIs ejecutivos existentes.", ["RISK_ANALYST", "ADMIN"], {}, {"overview": "object"}, get_bi_overview_tool),
        AssistantTool("get_top_corridors", "Consulta principales corredores existentes.", ["RISK_ANALYST", "ADMIN"], {}, {"corridors": "array"}, get_top_corridors_tool),
        AssistantTool("get_bi_customers", "Consulta clientes agregados de BI.", ["RISK_ANALYST", "ADMIN"], {}, {"customers": "object"}, get_bi_customers_tool),
        AssistantTool("get_forecast_summary", "Consulta forecast existente.", ["RISK_ANALYST", "ADMIN"], {}, {"forecast": "object"}, get_forecast_summary_tool),
        AssistantTool("get_risk_queue", "Consulta cola de riesgo autorizada.", ["RISK_ANALYST", "ADMIN"], {}, {"assessments": "array"}, get_risk_queue_tool),
        AssistantTool("get_risk_assessment", "Consulta snapshot de riesgo existente.", ["RISK_ANALYST", "ADMIN"], {"assessment_id": "integer?"}, {"assessment": "object|null"}, get_risk_assessment_tool),
        AssistantTool("get_blockchain_trace", "Consulta trazabilidad blockchain autorizada.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {"remittance_number": "string?"}, {"history": "array"}, get_blockchain_trace_tool),
        AssistantTool("verify_blockchain_evidence", "Verifica evidencia blockchain autorizada.", ["CLIENT", "RISK_ANALYST", "ADMIN"], {"remittance_number": "string?"}, {"verification": "object"}, verify_blockchain_evidence_tool),
    ]
    return {tool.name: tool for tool in tools}


def ensure_tool_allowed(tool: AssistantTool, user: User) -> None:
    if user.role.name not in tool.allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "ASSISTANT_ACCESS_DENIED", "message": "Tu perfil no tiene acceso a esta consulta"})


def get_support_article(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    article = search_knowledge(str(inputs.get("query", "")), user.role.name)
    return {"article": article, "sources": [{"type": "knowledge", "id": article["id"], "title": article["title"]}]}


def get_my_remittances(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    transactions = list_sent_transactions(db, user.id) + list_received_transactions(db, user.id)
    transactions.sort(key=lambda item: (item.created_at, item.id), reverse=True)
    return {"remittances": [_transaction_summary(item) for item in transactions[:5]], "sources": [{"type": "remittance", "id": item.id} for item in transactions[:5]]}


def get_remittance_status(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    transaction = _authorized_transaction(db, user, inputs)
    return {"remittance": _transaction_summary(transaction) if transaction else None, "sources": [{"type": "remittance", "id": transaction.id}] if transaction else []}


def get_remittance_fee(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    return get_remittance_status(db, user, inputs)


def get_bi_overview_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    overview = get_bi_overview(db, BIFilters())
    return {"overview": _jsonable(overview), "sources": [{"type": "bi", "id": "overview"}]}


def get_top_corridors_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    corridors = get_bi_corridors(db, BIFilters())
    return {"corridors": _jsonable(corridors[:5]), "sources": [{"type": "bi", "id": "corridors"}]}


def get_bi_customers_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    customers = get_bi_customers(db, BIFilters())
    return {"customers": _jsonable(customers), "sources": [{"type": "bi", "id": "customers"}]}


def get_forecast_summary_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    forecast = get_bi_forecast()
    return {"forecast": _jsonable(forecast), "sources": [{"type": "forecast", "id": forecast.get("model_version", "remittance-forecast-v1")}]}


def get_risk_queue_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    assessments = list_assessments(db, only_pending=True)
    if not assessments:
        assessments = list_assessments(db, only_pending=False)
    data = [_assessment_summary(item) for item in assessments[:5]]
    return {"assessments": data, "sources": [{"type": "risk_assessment", "id": item["id"]} for item in data]}


def get_risk_assessment_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    assessment_id = inputs.get("assessment_id")
    assessment = get_assessment_or_404(db, int(assessment_id)) if assessment_id else _latest_risk_assessment(db)
    if assessment is None:
        return {"assessment": None, "sources": []}
    return {"assessment": _assessment_summary(assessment), "sources": [{"type": "risk_assessment", "id": assessment.id}]}


def get_blockchain_trace_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    transaction = _authorized_transaction(db, user, inputs)
    if transaction is None:
        return {"history": [], "sources": []}
    history = transaction_history(db, transaction.id)
    return {
        "history": [{"block_index": block.block_index, "event_type": block.event_type, "block_hash": block.block_hash[:12]} for block in history],
        "sources": [{"type": "blockchain", "id": block.block_index} for block in history],
    }


def verify_blockchain_evidence_tool(db: Session, user: User, inputs: dict[str, Any]) -> dict[str, Any]:
    transaction = _authorized_transaction(db, user, inputs)
    if transaction is None:
        return {"verification": {"status": "NOT_FOUND", "verified": 0, "mismatches": []}, "sources": []}
    verification = verify_transaction_evidence(db, transaction.id)
    return {"verification": verification, "sources": [{"type": "blockchain", "id": f"remittance:{transaction.id}"}]}


def _authorized_transaction(db: Session, user: User, inputs: dict[str, Any]) -> Transaction | None:
    remittance_number = inputs.get("remittance_number")
    if remittance_number:
        if user.role.name == "CLIENT":
            return get_transaction_by_number(db, str(remittance_number), user.id)
        return db.scalar(
            select(Transaction)
            .options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender))
            .where(Transaction.transaction_id == str(remittance_number))
        )
    if user.role.name == "CLIENT":
        transactions = list_sent_transactions(db, user.id) + list_received_transactions(db, user.id)
        transactions.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return transactions[0] if transactions else None
    return db.scalar(select(Transaction).options(joinedload(Transaction.beneficiary), joinedload(Transaction.sender)).order_by(Transaction.created_at.desc(), Transaction.id.desc()))


def _latest_risk_assessment(db: Session) -> RiskAssessment | None:
    return db.scalar(select(RiskAssessment).order_by(RiskAssessment.final_risk_score.desc().nullslast(), RiskAssessment.evaluated_at.desc()))


def _transaction_summary(transaction: Transaction) -> dict[str, Any]:
    return {
        "id": transaction.id,
        "remittance_number": transaction.transaction_id,
        "status": transaction.status,
        "status_label": _status_label(transaction.status),
        "origin_country": transaction.origin_country,
        "destination_country": transaction.destination_country,
        "source_amount": _money(transaction.source_amount),
        "source_currency": transaction.source_currency,
        "destination_amount": _money(transaction.destination_amount),
        "destination_currency": transaction.destination_currency,
        "commission_amount": _money(transaction.commission_amount),
        "debit_amount": _money(transaction.debit_amount or transaction.total_amount),
        "debit_currency": transaction.debit_currency or transaction.source_currency,
        "created_at": transaction.created_at.isoformat(),
    }


def _assessment_summary(assessment: Any) -> dict[str, Any]:
    return {
        "id": assessment.id,
        "remittance_id": assessment.remittance_id,
        "remittance_number": getattr(assessment, "remittance_number", None) or getattr(getattr(assessment, "transaction", None), "transaction_id", None),
        "rule_score": _optional_number(assessment.rule_score),
        "ml_probability": _optional_number(assessment.ml_probability),
        "anomaly_score": _optional_number(assessment.anomaly_score),
        "final_risk_score": _optional_number(assessment.final_risk_score),
        "risk_band": assessment.risk_band,
        "recommended_action": assessment.recommended_action,
        "risk_engine_version": assessment.risk_engine_version,
        "review_status": assessment.review_status,
        "triggered_rules": getattr(assessment, "triggered_rules_json", None) or [],
        "explanations": getattr(assessment, "explanations_json", None) or [],
    }


def _status_label(status: str) -> str:
    return {
        "CREATED": "Creada",
        "VALIDATING": "Validando",
        "RISK_ANALYSIS": "Analizando riesgo",
        "APPROVED": "Aprobada",
        "PROCESSING": "Procesando",
        "AVAILABLE": "Disponible",
        "COMPLETED": "Completada",
        "REVIEW_REQUIRED": "Requiere revision",
        "REJECTED": "Rechazada",
    }.get(status, status)


def _money(value: Decimal | None) -> str:
    return f"{Decimal(value or 0):.2f}"


def _optional_number(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
