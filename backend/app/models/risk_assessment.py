from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    remittance_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False, index=True)
    assessment_sequence: Mapped[int] = mapped_column(default=1, nullable=False)

    rule_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    rules_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    triggered_rules_json: Mapped[list | None] = mapped_column(JSON, nullable=True)

    ml_probability: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    ml_model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ml_threshold: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    anomaly_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    anomaly_model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)

    final_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_band: Mapped[str] = mapped_column(String(30), nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(40), nullable=False)

    risk_engine_version: Mapped[str] = mapped_column(String(80), nullable=False)
    weights_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_band_thresholds_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    signal_status_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    explanations_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    review_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    review_decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    transaction = relationship("Transaction")
    analyst = relationship("User", foreign_keys=[reviewed_by])
