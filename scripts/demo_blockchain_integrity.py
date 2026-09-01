from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.blockchain.local_provider import LocalBlockchainProvider
from app.db.session import Base
from app.models.blockchain import BlockchainBlock


def main() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    DemoSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    provider = LocalBlockchainProvider(difficulty=1)

    with DemoSession() as db:
        provider.ensure_genesis(db)
        for index in range(1, 5):
            provider.record_evidence(
                db,
                {
                    "schema_version": "remittance-evidence-v1",
                    "event_type": "REMITTANCE_CREATED",
                    "entity_type": "remittance",
                    "entity_reference": f"demo-{index}",
                    "remittance_number": f"DEMO-{index}",
                    "origin_country": "Guatemala",
                    "destination_country": "Estados Unidos",
                    "source_currency": "GTQ",
                    "destination_currency": "USD",
                    "source_amount": "100",
                    "commission_amount": "2.25",
                    "status": "AVAILABLE",
                    "occurred_at": "2026-01-01T00:00:00Z",
                },
            )
        db.commit()
        before = provider.validate_chain(db)
        block = db.query(BlockchainBlock).filter(BlockchainBlock.block_index == 3).one()
        block.evidence_hash = "f" * 64
        db.commit()
        after = provider.validate_chain(db)
        print("Before tampering:")
        print(f"Chain valid: {str(before['valid']).upper()}")
        print()
        print("After tampering:")
        print(f"Chain valid: {str(after['valid']).upper()}")
        affected = after["errors"][0]["block_index"] if after["errors"] else "none"
        print(f"Affected block: {affected}")


if __name__ == "__main__":
    main()
