from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.blockchain.config import BLOCKCHAIN_ENGINE_VERSION, DEFAULT_DIFFICULTY, HASH_ALGORITHM, SUPPORTED_SCHEMA_VERSIONS
from app.blockchain.evidence import remittance_evidence, risk_evidence
from app.blockchain.local_provider import local_blockchain_provider
from app.models.blockchain import BlockchainBlock
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction
from app.services.audit import log_audit_event


def record_remittance_event(db: Session, transaction: Transaction, event_type: str, actor_user_id: int | None = None) -> BlockchainBlock | None:
    try:
        occurred_at = transaction.updated_at if event_type == "REMITTANCE_COMPLETED" else transaction.created_at
        status_override = "COMPLETED" if event_type == "REMITTANCE_COMPLETED" else "AVAILABLE"
        block = local_blockchain_provider.record_evidence(db, remittance_evidence(transaction, event_type, occurred_at, status_override))
        log_audit_event(
            db,
            user_id=actor_user_id,
            action="BLOCKCHAIN_EVIDENCE_RECORDED",
            entity="blockchain_block",
            entity_id=str(block.block_index),
            metadata={"event_type": event_type, "entity_type": "remittance", "entity_reference": str(transaction.id)},
        )
        return block
    except Exception as exc:
        log_audit_event(
            db,
            user_id=actor_user_id,
            action="BLOCKCHAIN_EVIDENCE_FAILED",
            entity="transaction",
            entity_id=str(transaction.id),
            metadata={"event_type": event_type, "error": str(exc)},
        )
        return None


def record_risk_event(db: Session, assessment: RiskAssessment, actor_user_id: int | None = None) -> BlockchainBlock | None:
    try:
        block = local_blockchain_provider.record_evidence(db, risk_evidence(assessment))
        log_audit_event(
            db,
            user_id=actor_user_id,
            action="BLOCKCHAIN_EVIDENCE_RECORDED",
            entity="blockchain_block",
            entity_id=str(block.block_index),
            metadata={"event_type": "RISK_ASSESSMENT_RECORDED", "entity_reference": str(assessment.remittance_id)},
        )
        return block
    except Exception as exc:
        log_audit_event(
            db,
            user_id=actor_user_id,
            action="BLOCKCHAIN_EVIDENCE_FAILED",
            entity="risk_assessment",
            entity_id=str(assessment.id),
            metadata={"event_type": "RISK_ASSESSMENT_RECORDED", "error": str(exc)},
        )
        return None


def backfill_blockchain_evidence(db: Session, actor_user_id: int | None = None) -> dict[str, int]:
    before_count = db.query(BlockchainBlock).count()
    transactions = list(db.scalars(select(Transaction).order_by(Transaction.id)))
    assessments = list(db.scalars(select(RiskAssessment).order_by(RiskAssessment.remittance_id, RiskAssessment.assessment_sequence, RiskAssessment.id)))
    assessments_by_transaction: dict[int, list[RiskAssessment]] = {}
    for assessment in assessments:
        assessments_by_transaction.setdefault(assessment.remittance_id, []).append(assessment)

    for transaction in transactions:
        record_remittance_event(db, transaction, "REMITTANCE_CREATED", actor_user_id)
        record_remittance_event(db, transaction, "REMITTANCE_AVAILABLE", actor_user_id)
        for assessment in assessments_by_transaction.get(transaction.id, []):
            record_risk_event(db, assessment, actor_user_id)
        if transaction.status == "COMPLETED":
            record_remittance_event(db, transaction, "REMITTANCE_COMPLETED", actor_user_id)

    db.flush()
    after_count = db.query(BlockchainBlock).count()
    return {
        "transactions_scanned": len(transactions),
        "risk_assessments_scanned": len(assessments),
        "blocks_before": before_count,
        "blocks_after": after_count,
        "blocks_created": after_count - before_count,
    }


def blockchain_info(db: Session) -> dict[str, Any]:
    chain = local_blockchain_provider.get_chain(db)
    validation = local_blockchain_provider.validate_chain(db)
    return {
        "blockchain_engine_version": BLOCKCHAIN_ENGINE_VERSION,
        "hash_algorithm": HASH_ALGORITHM,
        "difficulty": DEFAULT_DIFFICULTY,
        "total_blocks": len(chain),
        "total_evidence": len([block for block in chain if block.event_type != "GENESIS"]),
        "genesis_hash": chain[0].block_hash if chain else None,
        "last_block_hash": chain[-1].block_hash if chain else None,
        "chain_valid": validation["valid"],
        "supported_schema_versions": sorted(SUPPORTED_SCHEMA_VERSIONS),
    }


def blockchain_metrics(db: Session) -> dict[str, Any]:
    chain = local_blockchain_provider.get_chain(db)
    validation = local_blockchain_provider.validate_chain(db)
    event_counts = Counter(block.event_type for block in chain if block.event_type != "GENESIS")
    mining_times = [block.mining_time_ms for block in chain if block.event_type != "GENESIS"]
    return {
        "total_blocks": len(chain),
        "total_evidence": sum(event_counts.values()),
        "blocks_by_event_type": dict(event_counts),
        "chain_valid": validation["valid"],
        "last_block_timestamp": chain[-1].timestamp if chain else None,
        "average_mining_time_ms": round(sum(mining_times) / len(mining_times), 2) if mining_times else None,
    }


def list_blocks(db: Session) -> list[BlockchainBlock]:
    return local_blockchain_provider.get_chain(db)


def get_block_by_index(db: Session, block_index: int) -> BlockchainBlock | None:
    return local_blockchain_provider.get_block(db, block_index)


def transaction_history(db: Session, remittance_id: int) -> list[BlockchainBlock]:
    return local_blockchain_provider.get_entity_history(db, str(remittance_id))


def verify_transaction_evidence(db: Session, remittance_id: int) -> dict[str, Any]:
    return local_blockchain_provider.verify_evidence(db, str(remittance_id))


def validate_blockchain(db: Session) -> dict[str, Any]:
    return local_blockchain_provider.validate_chain(db)


def blocks_by_event_type(db: Session) -> dict[str, int]:
    return dict(Counter(block.event_type for block in db.scalars(select(BlockchainBlock)).all()))
