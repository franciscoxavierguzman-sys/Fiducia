from __future__ import annotations

from datetime import datetime

from app.blockchain.config import LEGACY_REMITTANCE_EVIDENCE_SCHEMA, REMITTANCE_EVIDENCE_SCHEMA, RISK_EVIDENCE_SCHEMA
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction


def remittance_evidence(
    transaction: Transaction,
    event_type: str,
    occurred_at: datetime | None = None,
    status_override: str | None = None,
    schema_version: str = REMITTANCE_EVIDENCE_SCHEMA,
) -> dict:
    evidence = {
        "schema_version": schema_version,
        "event_type": event_type,
        "entity_type": "remittance",
        "entity_reference": str(transaction.id),
        "remittance_number": transaction.transaction_id,
        "origin_country": transaction.origin_country,
        "destination_country": transaction.destination_country,
        "source_currency": transaction.source_currency,
        "destination_currency": transaction.destination_currency,
        "source_amount": transaction.source_amount,
        "commission_amount": transaction.commission_amount,
        "status": status_override or transaction.status,
        "occurred_at": occurred_at or transaction.updated_at or transaction.created_at,
    }
    if schema_version != LEGACY_REMITTANCE_EVIDENCE_SCHEMA:
        evidence.update(
            {
                "sender_id": transaction.sender_id,
                "beneficiary_id": transaction.beneficiary_id,
                "beneficiary_user_id": transaction.beneficiary_user_id,
                "funding_source_id": transaction.funding_source_id,
                "exchange_rate": transaction.exchange_rate,
                "total_amount": transaction.total_amount,
                "debit_amount": transaction.debit_amount,
                "debit_currency": transaction.debit_currency,
                "destination_amount": transaction.destination_amount,
                "payment_method": transaction.payment_method,
                "delivery_method": transaction.delivery_method,
            }
        )
    return evidence


def risk_evidence(assessment: RiskAssessment) -> dict:
    return {
        "schema_version": RISK_EVIDENCE_SCHEMA,
        "event_type": "RISK_ASSESSMENT_RECORDED",
        "entity_type": "risk_assessment",
        "entity_reference": str(assessment.remittance_id),
        "risk_assessment_id": assessment.id,
        "risk_engine_version": assessment.risk_engine_version,
        "rules_version": assessment.rules_version,
        "ml_model_version": assessment.ml_model_version,
        "anomaly_model_version": assessment.anomaly_model_version,
        "final_risk_score": assessment.final_risk_score,
        "risk_band": assessment.risk_band,
        "evaluated_at": assessment.evaluated_at,
    }


def idempotency_key(entity_type: str, entity_reference: str, event_type: str, schema_version: str) -> str:
    return f"{entity_type}:{entity_reference}:{event_type}:{schema_version}"


def evidence_idempotency_key(evidence: dict) -> str:
    event_type = str(evidence["event_type"])
    schema_version = str(evidence["schema_version"])
    if event_type == "RISK_ASSESSMENT_RECORDED" and evidence.get("risk_assessment_id") is not None:
        return f"risk_assessment:{evidence['risk_assessment_id']}:{event_type}:{schema_version}"
    return idempotency_key(str(evidence["entity_type"]), str(evidence["entity_reference"]), event_type, schema_version)
