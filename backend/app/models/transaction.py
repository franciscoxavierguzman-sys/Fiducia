from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    remittance_uuid: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True, index=True)
    transaction_id: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    beneficiary_id: Mapped[int] = mapped_column(ForeignKey("beneficiaries.id"), nullable=False, index=True)
    beneficiary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    funding_source_id: Mapped[int | None] = mapped_column(ForeignKey("funding_sources.id"), nullable=True, index=True)
    origin_country: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_country: Mapped[str] = mapped_column(String(100), nullable=False)
    source_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    debit_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    debit_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    destination_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="CREATED")
    rule_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    ml_probability: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    anomaly_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    final_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    sender = relationship("User", foreign_keys=[sender_id])
    beneficiary_user = relationship("User", foreign_keys=[beneficiary_user_id])
    funding_source = relationship("FundingSource")
    beneficiary = relationship("Beneficiary", back_populates="transactions")
    status_history = relationship("RemittanceStatusHistory", back_populates="transaction")
