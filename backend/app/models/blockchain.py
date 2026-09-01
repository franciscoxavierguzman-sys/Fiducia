from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BlockchainBlock(Base):
    __tablename__ = "blockchain_blocks"
    __table_args__ = (
        UniqueConstraint("block_index", name="uq_blockchain_block_index"),
        UniqueConstraint("block_hash", name="uq_blockchain_block_hash"),
        UniqueConstraint("idempotency_key", name="uq_blockchain_idempotency_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    block_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String(40), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_reference: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    evidence_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    block_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(80), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    record_status: Mapped[str] = mapped_column(String(30), nullable=False, default="RECORDED")
    mining_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
