from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TriggeredRule(BaseModel):
    rule_id: str
    rule_code: str
    name: str
    description: str
    severity: str
    contribution: int
    reason: str
    version: str


class RiskAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    remittance_id: int
    assessment_sequence: int
    rule_score: Decimal | None
    rules_version: str | None
    triggered_rules_json: list[dict[str, Any]] | None
    ml_probability: Decimal | None
    ml_model_version: str | None
    ml_threshold: Decimal | None
    anomaly_score: Decimal | None
    anomaly_model_version: str | None
    final_risk_score: Decimal | None
    risk_band: str
    recommended_action: str
    risk_engine_version: str
    weights_json: dict[str, Any] | None
    risk_band_thresholds_json: dict[str, Any] | None = None
    signal_status_json: dict[str, Any] | None
    explanations_json: list[str] | None
    evaluated_at: datetime
    review_status: str
    reviewed_by: int | None
    review_decision: str | None
    review_reason: str | None
    reviewed_at: datetime | None


class RiskAssessmentWithRemittance(RiskAssessmentRead):
    remittance_number: str | None
    sender_name: str
    beneficiary_name: str
    origin_country: str
    destination_country: str
    source_amount: Decimal
    source_currency: str
    status: str
    created_at: datetime


class RiskReviewRequest(BaseModel):
    decision: Literal["APPROVE", "ESCALATE", "REJECT"]
    reason: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_reason_for_non_approve(self):
        if self.decision in {"ESCALATE", "REJECT"} and not (self.reason or "").strip():
            raise ValueError("La justificacion es obligatoria para escalar o rechazar.")
        if self.reason:
            self.reason = self.reason.strip()
        return self


class RiskEngineInfo(BaseModel):
    version: str
    aggregation_strategy: str
    weights: dict[str, float]
    risk_band_thresholds: dict[str, float]
    rules_version: str
    ml_model_version: str | None
    ml_threshold: float | None
    anomaly_model_version: str | None
    anomaly_available: bool


class RiskDashboardMetrics(BaseModel):
    total_assessments: int
    low_risk: int
    medium_risk: int
    high_risk: int
    pending_review: int
    reviewed: int
    approved: int
    escalated: int
    rejected: int
    average_rule_score: float | None
    average_ml_probability: float | None
    average_anomaly_score: float | None
    average_final_risk_score: float | None
    top_triggered_rules: list[dict[str, Any]]
