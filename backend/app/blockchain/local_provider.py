from __future__ import annotations

import time
from threading import RLock
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.blockchain.canonical import canonical_json
from app.blockchain.config import (
    BLOCKCHAIN_ENGINE_VERSION,
    DEFAULT_DIFFICULTY,
    GENESIS_ENTITY_REFERENCE,
    GENESIS_ENTITY_TYPE,
    GENESIS_EVENT_TYPE,
    GENESIS_PREVIOUS_HASH,
    GENESIS_SCHEMA_VERSION,
    HASH_ALGORITHM,
    SUPPORTED_SCHEMA_VERSIONS,
)
from app.blockchain.evidence import evidence_idempotency_key, idempotency_key
from app.blockchain.hash import hash_payload, is_sha256_hex, sha256_hex
from app.blockchain.provider import BlockchainProvider
from app.models.blockchain import BlockchainBlock
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction


class LocalBlockchainProvider(BlockchainProvider):
    def __init__(self, difficulty: int = DEFAULT_DIFFICULTY):
        self.difficulty = difficulty
        self._write_lock = RLock()

    def record_evidence(self, db: Session, evidence: dict[str, Any]) -> BlockchainBlock:
        with self._write_lock:
            self.ensure_genesis(db)
            schema_version = str(evidence["schema_version"])
            event_type = str(evidence["event_type"])
            entity_type = str(evidence["entity_type"])
            entity_reference = str(evidence["entity_reference"])
            key = evidence_idempotency_key(evidence)
            existing = db.scalar(select(BlockchainBlock).where(BlockchainBlock.idempotency_key == key))
            if existing is not None:
                return existing

            latest = self._latest_block(db)
            index = int(latest.block_index) + 1 if latest else 0
            evidence_hash = hash_payload(evidence)
            timestamp = _utc_now()
            block = self._build_block(
                index=index,
                timestamp=timestamp,
                event_type=event_type,
                entity_type=entity_type,
                entity_reference=entity_reference,
                evidence_hash=evidence_hash,
                previous_hash=latest.block_hash if latest else GENESIS_PREVIOUS_HASH,
                schema_version=schema_version,
                idempotency_key=key,
                difficulty=self.difficulty,
            )
            db.add(block)
            db.flush()
            return block

    def ensure_genesis(self, db: Session) -> BlockchainBlock:
        with self._write_lock:
            genesis = db.scalar(select(BlockchainBlock).where(BlockchainBlock.block_index == 0))
            if genesis is not None:
                return genesis
            evidence = {
                "schema_version": GENESIS_SCHEMA_VERSION,
                "event_type": GENESIS_EVENT_TYPE,
                "entity_type": GENESIS_ENTITY_TYPE,
                "entity_reference": GENESIS_ENTITY_REFERENCE,
                "description": "FIDUCIA local blockchain genesis block",
            }
            block = self._build_block(
                index=0,
                timestamp="2026-01-01T00:00:00Z",
                event_type=GENESIS_EVENT_TYPE,
                entity_type=GENESIS_ENTITY_TYPE,
                entity_reference=GENESIS_ENTITY_REFERENCE,
                evidence_hash=hash_payload(evidence),
                previous_hash=GENESIS_PREVIOUS_HASH,
                schema_version=GENESIS_SCHEMA_VERSION,
                idempotency_key=idempotency_key(GENESIS_ENTITY_TYPE, GENESIS_ENTITY_REFERENCE, GENESIS_EVENT_TYPE, GENESIS_SCHEMA_VERSION),
                difficulty=self.difficulty,
            )
            db.add(block)
            db.flush()
            return block

    def get_block(self, db: Session, block_index: int) -> BlockchainBlock | None:
        return db.scalar(select(BlockchainBlock).where(BlockchainBlock.block_index == block_index))

    def get_chain(self, db: Session) -> list[BlockchainBlock]:
        self.ensure_genesis(db)
        return list(db.scalars(select(BlockchainBlock).order_by(BlockchainBlock.block_index)))

    def get_entity_history(self, db: Session, entity_reference: str) -> list[BlockchainBlock]:
        self.ensure_genesis(db)
        return list(
            db.scalars(
                select(BlockchainBlock)
                .where(BlockchainBlock.entity_reference == str(entity_reference), BlockchainBlock.entity_type.in_(["remittance", "risk_assessment"]))
                .order_by(BlockchainBlock.block_index)
            )
        )

    def validate_chain(self, db: Session) -> dict[str, Any]:
        blocks = self.get_chain(db)
        errors = []
        for position, block in enumerate(blocks):
            if block.block_index != position:
                errors.append({"block_index": block.block_index, "code": "INVALID_INDEX"})
            if block.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
                errors.append({"block_index": block.block_index, "code": "UNSUPPORTED_EVIDENCE_SCHEMA"})
            if not is_sha256_hex(block.evidence_hash):
                errors.append({"block_index": block.block_index, "code": "INVALID_EVIDENCE_HASH"})
            if block.block_hash != calculate_block_hash(block):
                errors.append({"block_index": block.block_index, "code": "BLOCK_HASH_MISMATCH"})
            if not block.block_hash.startswith("0" * block.difficulty):
                errors.append({"block_index": block.block_index, "code": "POW_NOT_SATISFIED"})
            if position == 0:
                if block.event_type != GENESIS_EVENT_TYPE or block.previous_hash != GENESIS_PREVIOUS_HASH:
                    errors.append({"block_index": block.block_index, "code": "INVALID_GENESIS"})
            else:
                previous = blocks[position - 1]
                if block.previous_hash != previous.block_hash:
                    errors.append({"block_index": block.block_index, "code": "PREVIOUS_HASH_MISMATCH"})
            try:
                datetime.fromisoformat(block.timestamp.replace("Z", "+00:00"))
            except ValueError:
                errors.append({"block_index": block.block_index, "code": "INVALID_TIMESTAMP"})
        return {"valid": not errors, "blocks_checked": len(blocks), "errors": errors}

    def verify_evidence(self, db: Session, entity_reference: str) -> dict[str, Any]:
        blocks = self.get_entity_history(db, entity_reference)
        if not blocks:
            return {"status": "NOT_FOUND", "verified": 0, "mismatches": []}
        mismatches = []
        verified = 0
        for block in blocks:
            expected = rebuild_evidence_hash(db, block)
            if expected is None:
                return {"status": "UNSUPPORTED_SCHEMA", "verified": verified, "mismatches": [{"block_index": block.block_index}]}
            if expected != block.evidence_hash:
                mismatches.append({"block_index": block.block_index, "expected_hash": expected, "recorded_hash": block.evidence_hash})
            else:
                verified += 1
        return {"status": "MISMATCH" if mismatches else "VERIFIED", "verified": verified, "mismatches": mismatches}

    def _latest_block(self, db: Session) -> BlockchainBlock | None:
        max_index = db.scalar(select(func.max(BlockchainBlock.block_index)))
        if max_index is None:
            return None
        return db.scalar(select(BlockchainBlock).where(BlockchainBlock.block_index == max_index))

    def _build_block(
        self,
        *,
        index: int,
        timestamp: str,
        event_type: str,
        entity_type: str,
        entity_reference: str,
        evidence_hash: str,
        previous_hash: str,
        schema_version: str,
        idempotency_key: str,
        difficulty: int,
    ) -> BlockchainBlock:
        nonce = 0
        started = time.perf_counter()
        while True:
            header = block_header(index, timestamp, event_type, entity_type, entity_reference, evidence_hash, previous_hash, nonce, difficulty, schema_version)
            block_hash = sha256_hex(canonical_json(header))
            if block_hash.startswith("0" * difficulty):
                break
            nonce += 1
        return BlockchainBlock(
            block_index=index,
            timestamp=timestamp,
            event_type=event_type,
            entity_type=entity_type,
            entity_reference=entity_reference,
            evidence_hash=evidence_hash,
            previous_hash=previous_hash,
            nonce=nonce,
            difficulty=difficulty,
            block_hash=block_hash,
            schema_version=schema_version,
            idempotency_key=idempotency_key,
            record_status="RECORDED",
            mining_time_ms=int((time.perf_counter() - started) * 1000),
        )


def block_header(
    index: int,
    timestamp: str,
    event_type: str,
    entity_type: str,
    entity_reference: str,
    evidence_hash: str,
    previous_hash: str,
    nonce: int,
    difficulty: int,
    schema_version: str,
) -> dict[str, Any]:
    return {
        "index": index,
        "timestamp": timestamp,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_reference": entity_reference,
        "evidence_hash": evidence_hash,
        "previous_hash": previous_hash,
        "nonce": nonce,
        "difficulty": difficulty,
        "schema_version": schema_version,
    }


def calculate_block_hash(block: BlockchainBlock) -> str:
    header = block_header(
        block.block_index,
        block.timestamp,
        block.event_type,
        block.entity_type,
        block.entity_reference,
        block.evidence_hash,
        block.previous_hash,
        block.nonce,
        block.difficulty,
        block.schema_version,
    )
    return sha256_hex(canonical_json(header))


def rebuild_evidence_hash(db: Session, block: BlockchainBlock) -> str | None:
    from app.blockchain.evidence import remittance_evidence, risk_evidence

    if block.schema_version == GENESIS_SCHEMA_VERSION:
        return block.evidence_hash
    if block.schema_version.endswith("remittance-evidence-v1"):
        transaction = db.get(Transaction, int(block.entity_reference))
        if transaction is None:
            return None
        occurred_at = transaction.updated_at if block.event_type == "REMITTANCE_COMPLETED" else transaction.created_at
        status_override = "COMPLETED" if block.event_type == "REMITTANCE_COMPLETED" else "AVAILABLE"
        return hash_payload(remittance_evidence(transaction, block.event_type, occurred_at, status_override))
    if block.schema_version.endswith("risk-evidence-v1"):
        assessments = list(
            db.scalars(
                select(RiskAssessment)
                .where(RiskAssessment.remittance_id == int(block.entity_reference))
                .order_by(RiskAssessment.assessment_sequence.desc(), RiskAssessment.id.desc())
            )
        )
        if not assessments:
            return None
        for assessment in assessments:
            candidate = hash_payload(risk_evidence(assessment))
            if candidate == block.evidence_hash:
                return candidate
        return hash_payload(risk_evidence(assessments[0]))
    return None


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


local_blockchain_provider = LocalBlockchainProvider()
