from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.blockchain.config import LEGACY_REMITTANCE_EVIDENCE_SCHEMA, REMITTANCE_EVIDENCE_SCHEMA
from app.blockchain.evidence import remittance_evidence
from app.blockchain.hash import hash_payload
from app.blockchain.local_provider import local_blockchain_provider, rebuild_evidence_hash
from app.models.blockchain import BlockchainBlock
from app.models.transaction import Transaction
from app.services.audit import log_audit_event


INTEGRITY_STATUSES = {
    "VERIFIED",
    "INTEGRITY_MISMATCH",
    "BLOCKCHAIN_RECORD_MISSING",
    "DATABASE_RECORD_MISSING",
    "LEGACY_NOT_PROTECTED",
    "CHAIN_BROKEN",
    "VERIFICATION_ERROR",
}

PROTECTED_REMITTANCE_FIELDS = [
    "schema_version",
    "event_type",
    "entity_type",
    "entity_reference",
    "sender_id",
    "beneficiary_id",
    "beneficiary_user_id",
    "funding_source_id",
    "remittance_number",
    "origin_country",
    "destination_country",
    "source_currency",
    "destination_currency",
    "source_amount",
    "commission_amount",
    "exchange_rate",
    "total_amount",
    "debit_amount",
    "debit_currency",
    "destination_amount",
    "payment_method",
    "delivery_method",
    "status",
    "occurred_at",
]


def canonicalize_transaction(transaction: Transaction, event_type: str, occurred_at: datetime | None = None, status_override: str | None = None) -> dict[str, Any]:
    return remittance_evidence(transaction, event_type, occurred_at, status_override)


def calculate_transaction_hash(canonical_data: dict[str, Any]) -> str:
    return hash_payload(canonical_data)


def verify_transaction_integrity(db: Session, transaction_id: int, actor_user_id: int | None = None, verification_source: str = "API") -> dict[str, Any]:
    verified_at = _utc_now()
    try:
        chain_validation = local_blockchain_provider.validate_chain(db)
        if not chain_validation["valid"]:
            return {
                "transaction_id": str(transaction_id),
                "remittance_number": None,
                "status": "CHAIN_BROKEN",
                "stored_hash": None,
                "calculated_hash": None,
                "verified_at": verified_at,
                "blockchain_reference": None,
                "details": "La cadena local presenta inconsistencias de enlace, hash o prueba de trabajo.",
                "differences": [],
                "blocks_checked": chain_validation["blocks_checked"],
            }

        transaction = db.get(Transaction, transaction_id)
        blocks = _remittance_blocks(db, transaction_id)
        if transaction is None:
            return {
                "transaction_id": str(transaction_id),
                "remittance_number": None,
                "status": "DATABASE_RECORD_MISSING" if blocks else "VERIFICATION_ERROR",
                "stored_hash": blocks[-1].evidence_hash if blocks else None,
                "calculated_hash": None,
                "verified_at": verified_at,
                "blockchain_reference": _block_reference(blocks[-1]) if blocks else None,
                "details": "Existe evidencia blockchain para una remesa que ya no existe en la base de datos." if blocks else "No existe remesa ni evidencia blockchain para el ID indicado.",
                "differences": [],
                "blocks_checked": len(blocks),
            }

        if not blocks:
            status = _missing_evidence_status(db, transaction)
            return {
                "transaction_id": str(transaction.id),
                "remittance_number": transaction.transaction_id,
                "status": status,
                "stored_hash": None,
                "calculated_hash": None,
                "verified_at": verified_at,
                "blockchain_reference": None,
                "details": "La remesa no tiene evidencia blockchain asociada." if status == "BLOCKCHAIN_RECORD_MISSING" else "Remesa creada antes de contar con evidencia blockchain verificable.",
                "differences": [],
                "blocks_checked": 0,
            }

        mismatches = []
        verified_blocks = 0
        for block in blocks:
            calculated = rebuild_evidence_hash(db, block)
            if calculated is None:
                mismatches.append(_mismatch(block, None, "No fue posible reconstruir la evidencia canonica para este bloque."))
            elif calculated != block.evidence_hash:
                mismatches.append(
                    _mismatch(
                        block,
                        calculated,
                        "La informacion actual de base de datos no coincide con la evidencia criptografica registrada.",
                    )
                )
            else:
                verified_blocks += 1

        if mismatches:
            first = mismatches[0]
            log_audit_event(
                db,
                user_id=actor_user_id,
                action="BLOCKCHAIN_INTEGRITY_MISMATCH",
                entity="transaction",
                entity_id=str(transaction.id),
                metadata={
                    "transaction_id": transaction.transaction_id,
                    "stored_hash": first["stored_hash"],
                    "calculated_hash": first["calculated_hash"],
                    "detected_at": verified_at,
                    "verification_source": verification_source,
                },
            )
            return {
                "transaction_id": str(transaction.id),
                "remittance_number": transaction.transaction_id,
                "status": "INTEGRITY_MISMATCH",
                "stored_hash": first["stored_hash"],
                "calculated_hash": first["calculated_hash"],
                "verified_at": verified_at,
                "blockchain_reference": first["blockchain_reference"],
                "details": "Se detecto una modificacion, pero la evidencia criptografica disponible no permite determinar que campo fue alterado.",
                "differences": [],
                "blocks_checked": len(blocks),
                "verified_blocks": verified_blocks,
                "mismatches": mismatches,
            }

        latest = blocks[-1]
        latest_hash = rebuild_evidence_hash(db, latest)
        return {
            "transaction_id": str(transaction.id),
            "remittance_number": transaction.transaction_id,
            "status": "VERIFIED",
            "stored_hash": latest.evidence_hash,
            "calculated_hash": latest_hash,
            "verified_at": verified_at,
            "blockchain_reference": _block_reference(latest),
            "details": None,
            "differences": [],
            "blocks_checked": len(blocks),
            "verified_blocks": verified_blocks,
            "mismatches": [],
        }
    except Exception as exc:
        return {
            "transaction_id": str(transaction_id),
            "remittance_number": None,
            "status": "VERIFICATION_ERROR",
            "stored_hash": None,
            "calculated_hash": None,
            "verified_at": verified_at,
            "blockchain_reference": None,
            "details": f"No fue posible completar la verificacion: {exc}",
            "differences": [],
            "blocks_checked": 0,
        }


def verify_blockchain_integrity(db: Session, actor_user_id: int | None = None, verification_source: str = "API") -> dict[str, Any]:
    verified_at = _utc_now()
    chain_validation = local_blockchain_provider.validate_chain(db)
    transactions = list(db.scalars(select(Transaction).order_by(Transaction.id)))
    results = [
        verify_transaction_integrity(db, transaction.id, actor_user_id=actor_user_id, verification_source=verification_source)
        for transaction in transactions
    ]
    counts = {status: 0 for status in INTEGRITY_STATUSES}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1

    missing_database = _database_missing_results(db, {transaction.id for transaction in transactions}, verified_at)
    for result in missing_database:
        counts[result["status"]] = counts.get(result["status"], 0) + 1

    total_checked = len(results) + len(missing_database)
    return {
        "status": "VERIFIED" if chain_validation["valid"] and counts.get("INTEGRITY_MISMATCH", 0) == 0 and counts.get("BLOCKCHAIN_RECORD_MISSING", 0) == 0 and counts.get("DATABASE_RECORD_MISSING", 0) == 0 else "REVIEW_REQUIRED",
        "verified_at": verified_at,
        "total_transactions": total_checked,
        "verified": counts.get("VERIFIED", 0),
        "integrity_mismatches": counts.get("INTEGRITY_MISMATCH", 0),
        "blockchain_record_missing": counts.get("BLOCKCHAIN_RECORD_MISSING", 0),
        "database_record_missing": counts.get("DATABASE_RECORD_MISSING", 0),
        "legacy_not_protected": counts.get("LEGACY_NOT_PROTECTED", 0),
        "chain_broken": 0 if chain_validation["valid"] else 1,
        "verification_errors": counts.get("VERIFICATION_ERROR", 0),
        "chain_validation": chain_validation,
        "results": results + missing_database,
    }


def latest_integrity_status(db: Session) -> dict[str, Any]:
    return verify_blockchain_integrity(db, verification_source="STATUS")


def _remittance_blocks(db: Session, transaction_id: int) -> list[BlockchainBlock]:
    return list(
        db.scalars(
            select(BlockchainBlock)
            .where(
                BlockchainBlock.entity_type == "remittance",
                BlockchainBlock.entity_reference == str(transaction_id),
                BlockchainBlock.schema_version.in_([LEGACY_REMITTANCE_EVIDENCE_SCHEMA, REMITTANCE_EVIDENCE_SCHEMA]),
            )
            .order_by(BlockchainBlock.block_index)
        )
    )


def _missing_evidence_status(db: Session, transaction: Transaction) -> str:
    first_remittance_block = db.scalars(
        select(BlockchainBlock)
        .where(BlockchainBlock.entity_type == "remittance", BlockchainBlock.schema_version.in_([LEGACY_REMITTANCE_EVIDENCE_SCHEMA, REMITTANCE_EVIDENCE_SCHEMA]))
        .order_by(BlockchainBlock.created_at, BlockchainBlock.block_index)
    ).first()
    if first_remittance_block is None:
        return "LEGACY_NOT_PROTECTED"
    return "LEGACY_NOT_PROTECTED" if transaction.created_at < first_remittance_block.created_at else "BLOCKCHAIN_RECORD_MISSING"


def _database_missing_results(db: Session, existing_transaction_ids: set[int], verified_at: str) -> list[dict[str, Any]]:
    entity_refs = set(
        db.scalars(
            select(BlockchainBlock.entity_reference)
            .where(BlockchainBlock.entity_type == "remittance", BlockchainBlock.schema_version.in_([LEGACY_REMITTANCE_EVIDENCE_SCHEMA, REMITTANCE_EVIDENCE_SCHEMA]))
        )
    )
    results = []
    for entity_ref in sorted(entity_refs, key=lambda item: int(item) if str(item).isdigit() else str(item)):
        if not str(entity_ref).isdigit() or int(entity_ref) in existing_transaction_ids:
            continue
        blocks = _remittance_blocks(db, int(entity_ref))
        latest = blocks[-1] if blocks else None
        results.append(
            {
                "transaction_id": str(entity_ref),
                "remittance_number": None,
                "status": "DATABASE_RECORD_MISSING",
                "stored_hash": latest.evidence_hash if latest else None,
                "calculated_hash": None,
                "verified_at": verified_at,
                "blockchain_reference": _block_reference(latest) if latest else None,
                "details": "Existe evidencia blockchain para una remesa que ya no existe en la base de datos.",
                "differences": [],
                "blocks_checked": len(blocks),
            }
        )
    return results


def _mismatch(block: BlockchainBlock, calculated_hash: str | None, details: str) -> dict[str, Any]:
    return {
        "block_index": block.block_index,
        "event_type": block.event_type,
        "stored_hash": block.evidence_hash,
        "calculated_hash": calculated_hash,
        "blockchain_reference": _block_reference(block),
        "details": details,
    }


def _block_reference(block: BlockchainBlock | None) -> str | None:
    return f"blockchain_blocks:{block.block_index}" if block is not None else None


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
