from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction
from app.models.user import User
from app.risk.aggregator import RISK_BAND_THRESHOLDS, RISK_ENGINE_VERSION, aggregate_risk, engine_metadata
from app.risk.anomaly import anomaly_model_info, predict_anomaly_score
from app.risk.features import build_operational_features
from app.risk.rules import RULES_VERSION, evaluate_rules
from app.schemas.risk_engine import RiskAssessmentWithRemittance
from app.services.audit import log_audit_event
from app.services.blockchain import record_risk_event
from app.services.ml_risk import get_model_info, predict_fraud_probability


def evaluate_remittance(db: Session, transaction: Transaction, *, actor_user_id: int | None = None, reevaluation: bool = False) -> RiskAssessment:
    features = build_operational_features(db, transaction)
    rule_result = _safe_rules(features)
    ml_result = _safe_ml(features)
    anomaly_result = _safe_anomaly(features)

    aggregated = aggregate_risk(
        rule_result.get("rule_score") if rule_result.get("available") else None,
        ml_result.get("ml_probability") if ml_result.get("available") else None,
        anomaly_result.get("anomaly_score") if anomaly_result.get("available") else None,
    )
    sequence = next_assessment_sequence(db, transaction.id)
    explanations = []
    explanations.extend(rule_result.get("explanations", []))
    explanations.extend(ml_result.get("explanations", []))
    explanations.extend(anomaly_result.get("explanations", []))
    explanations.extend(aggregated.explanations)

    assessment = RiskAssessment(
        remittance_id=transaction.id,
        assessment_sequence=sequence,
        rule_score=_decimal_or_none(rule_result.get("rule_score")),
        rules_version=rule_result.get("rules_version"),
        triggered_rules_json=rule_result.get("triggered_rules", []),
        ml_probability=_decimal_or_none(ml_result.get("ml_probability")),
        ml_model_version=ml_result.get("model_version"),
        ml_threshold=_decimal_or_none(ml_result.get("threshold")),
        anomaly_score=_decimal_or_none(anomaly_result.get("anomaly_score")),
        anomaly_model_version=anomaly_result.get("model_version"),
        final_risk_score=_decimal_or_none(aggregated.final_risk_score),
        risk_band=aggregated.risk_band,
        recommended_action=aggregated.recommended_action,
        risk_engine_version=RISK_ENGINE_VERSION,
        weights_json=aggregated.weights_used,
        risk_band_thresholds_json=RISK_BAND_THRESHOLDS,
        signal_status_json=aggregated.signal_status,
        explanations_json=explanations,
        review_status="PENDING" if aggregated.recommended_action in {"REVIEW", "MANUAL_REVIEW"} else "NOT_REQUIRED",
    )
    db.add(assessment)
    db.flush()

    transaction.rule_score = assessment.rule_score
    transaction.ml_probability = assessment.ml_probability
    transaction.anomaly_score = assessment.anomaly_score
    transaction.final_risk_score = assessment.final_risk_score
    transaction.risk_level = assessment.risk_band
    transaction.model_version = ml_result.get("model_version")

    log_audit_event(
        db,
        user_id=actor_user_id,
        action="RISK_ASSESSMENT_REEVALUATED" if reevaluation else "RISK_ASSESSMENT_CREATED",
        entity="risk_assessment",
        entity_id=str(assessment.id),
        metadata={
            "remittance_id": transaction.id,
            "remittance_number": transaction.transaction_id,
            "risk_band": assessment.risk_band,
            "recommended_action": assessment.recommended_action,
            "risk_engine_version": assessment.risk_engine_version,
            "risk_band_thresholds": assessment.risk_band_thresholds_json,
        },
    )
    record_risk_event(db, assessment, actor_user_id)
    return assessment


def next_assessment_sequence(db: Session, remittance_id: int) -> int:
    current = db.scalar(select(func.max(RiskAssessment.assessment_sequence)).where(RiskAssessment.remittance_id == remittance_id))
    return int(current or 0) + 1


def list_assessments(db: Session, *, only_pending: bool = False) -> list[RiskAssessmentWithRemittance]:
    query = (
        select(RiskAssessment)
        .options(
            joinedload(RiskAssessment.transaction).joinedload(Transaction.sender),
            joinedload(RiskAssessment.transaction).joinedload(Transaction.beneficiary),
        )
        .order_by(RiskAssessment.final_risk_score.desc().nullslast(), RiskAssessment.evaluated_at.desc())
    )
    if only_pending:
        query = query.where(RiskAssessment.review_status == "PENDING")
    return [_assessment_with_transaction(item) for item in db.scalars(query).unique()]


def get_assessment_or_404(db: Session, assessment_id: int) -> RiskAssessment:
    assessment = db.scalar(
        select(RiskAssessment)
        .options(
            joinedload(RiskAssessment.transaction).joinedload(Transaction.sender),
            joinedload(RiskAssessment.transaction).joinedload(Transaction.beneficiary),
        )
        .where(RiskAssessment.id == assessment_id)
    )
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "RISK_ASSESSMENT_NOT_FOUND", "message": "Evaluacion no encontrada"})
    return assessment


def get_latest_assessment_for_remittance(db: Session, remittance_id: int) -> RiskAssessment | None:
    return db.scalar(
        select(RiskAssessment)
        .where(RiskAssessment.remittance_id == remittance_id)
        .order_by(RiskAssessment.assessment_sequence.desc(), RiskAssessment.id.desc())
    )


def evaluate_remittance_by_id(db: Session, remittance_id: int, actor: User) -> RiskAssessment:
    transaction = db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.sender), joinedload(Transaction.beneficiary))
        .where(Transaction.id == remittance_id)
    )
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "TRANSACTION_NOT_FOUND", "message": "Remesa no encontrada"})
    assessment = evaluate_remittance(
        db,
        transaction,
        actor_user_id=actor.id,
        reevaluation=get_latest_assessment_for_remittance(db, remittance_id) is not None,
    )
    db.commit()
    db.refresh(assessment)
    return assessment


def review_assessment(db: Session, assessment_id: int, analyst: User, decision: str, reason: str | None) -> RiskAssessment:
    assessment = get_assessment_or_404(db, assessment_id)
    assessment.review_status = "REVIEWED"
    assessment.reviewed_by = analyst.id
    assessment.review_decision = decision
    assessment.review_reason = reason
    assessment.reviewed_at = datetime.now(UTC)
    log_audit_event(
        db,
        user_id=analyst.id,
        action="RISK_REVIEW_ESCALATED" if decision == "ESCALATE" else "RISK_REVIEW_COMPLETED",
        entity="risk_assessment",
        entity_id=str(assessment.id),
        metadata={"decision": decision, "risk_band": assessment.risk_band, "remittance_id": assessment.remittance_id},
    )
    db.commit()
    db.refresh(assessment)
    return assessment


def risk_engine_info() -> dict[str, Any]:
    metadata = engine_metadata()
    ml_info = get_model_info()
    anomaly_info = anomaly_model_info()
    return {
        **metadata,
        "rules_version": RULES_VERSION,
        "ml_model_version": ml_info.model_version,
        "ml_threshold": ml_info.threshold,
        "anomaly_model_version": anomaly_info.get("version") if anomaly_info.get("available") else None,
        "anomaly_available": bool(anomaly_info.get("available")),
    }


def risk_dashboard_metrics(db: Session) -> dict[str, Any]:
    assessments = list(db.scalars(select(RiskAssessment)))
    rule_counts: dict[str, int] = {}
    for assessment in assessments:
        for rule in assessment.triggered_rules_json or []:
            code = str(rule.get("rule_code", "UNKNOWN"))
            rule_counts[code] = rule_counts.get(code, 0) + 1
    return {
        "total_assessments": len(assessments),
        "low_risk": len([item for item in assessments if item.risk_band == "LOW"]),
        "medium_risk": len([item for item in assessments if item.risk_band == "MEDIUM"]),
        "high_risk": len([item for item in assessments if item.risk_band == "HIGH"]),
        "pending_review": len([item for item in assessments if item.review_status == "PENDING"]),
        "reviewed": len([item for item in assessments if item.review_status == "REVIEWED"]),
        "approved": len([item for item in assessments if item.review_decision == "APPROVE"]),
        "escalated": len([item for item in assessments if item.review_decision == "ESCALATE"]),
        "rejected": len([item for item in assessments if item.review_decision == "REJECT"]),
        "average_rule_score": _avg([item.rule_score for item in assessments]),
        "average_ml_probability": _avg([item.ml_probability for item in assessments]),
        "average_anomaly_score": _avg([item.anomaly_score for item in assessments]),
        "average_final_risk_score": _avg([item.final_risk_score for item in assessments]),
        "top_triggered_rules": [
            {"rule_code": code, "count": count} for code, count in sorted(rule_counts.items(), key=lambda item: item[1], reverse=True)[:8]
        ],
    }


def _safe_rules(features: dict[str, Any]) -> dict[str, Any]:
    try:
        result = evaluate_rules(features)
        result["explanations"] = [f"Rule Engine activo: {len(result['triggered_rules'])} reglas activadas."]
        return result
    except Exception as exc:
        return {"available": False, "rules_version": RULES_VERSION, "triggered_rules": [], "explanations": [f"Rule Engine no disponible: {exc}"]}


def _safe_ml(features: dict[str, Any]) -> dict[str, Any]:
    try:
        result = predict_fraud_probability(features)
        return {
            "available": True,
            "ml_probability": result.ml_probability,
            "model_version": result.model_version,
            "threshold": result.threshold,
            "classification": result.classification,
            "explanations": [f"ML genero probabilidad estimada {result.ml_probability:.4f} con threshold {result.threshold:.2f}."],
        }
    except Exception as exc:
        return {"available": False, "explanations": [f"ML no disponible para esta evaluacion: {exc}"]}


def _safe_anomaly(features: dict[str, Any]) -> dict[str, Any]:
    try:
        result = predict_anomaly_score(features)
        result["explanations"] = [f"Detector de anomalias genero score {result['anomaly_score']:.2f}/100."]
        return result
    except Exception as exc:
        return {"available": False, "explanations": [f"Anomaly Detection no disponible: {exc}"]}


def _assessment_with_transaction(assessment: RiskAssessment) -> RiskAssessmentWithRemittance:
    transaction = assessment.transaction
    return RiskAssessmentWithRemittance(
        **{name: getattr(assessment, name) for name in RiskAssessmentWithRemittance.model_fields if hasattr(assessment, name)},
        remittance_number=transaction.transaction_id,
        sender_name=f"{transaction.sender.first_name} {transaction.sender.last_name}" if transaction.sender else "",
        beneficiary_name=f"{transaction.beneficiary.first_name} {transaction.beneficiary.last_name}" if transaction.beneficiary else "",
        origin_country=transaction.origin_country,
        destination_country=transaction.destination_country,
        source_amount=transaction.source_amount,
        source_currency=transaction.source_currency,
        status=transaction.status,
        created_at=transaction.created_at,
    )


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _avg(values: list[Decimal | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 4)
