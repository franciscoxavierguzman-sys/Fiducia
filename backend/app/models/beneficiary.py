from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from app.db.session import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    beneficiary_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship_id: Mapped[int | None] = mapped_column(ForeignKey("beneficiary_relationships.id"), nullable=True, index=True)
    relationship_other: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Guatemala")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GTQ")
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    municipality: Mapped[str] = mapped_column(String(100), nullable=False)
    delivery_method: Mapped[str] = mapped_column(String(50), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    account_last_four: Mapped[str | None] = mapped_column(String(4), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    sender = orm_relationship("User", foreign_keys=[sender_id])
    beneficiary_user = orm_relationship("User", foreign_keys=[beneficiary_user_id])
    relationship_catalog = orm_relationship("BeneficiaryRelationship")
    transactions = orm_relationship("Transaction", back_populates="beneficiary")
