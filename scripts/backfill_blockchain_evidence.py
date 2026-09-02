from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ.setdefault("SECRET_KEY", "demo-data-local-secret")
os.environ["DATABASE_URL"] = f"sqlite:///{(ROOT / 'database' / 'fiducia.db').as_posix()}"

from app.db.session import Base, SessionLocal, engine
from app.db.sqlite_migrations import ensure_sqlite_schema_compatibility
from app.models import audit_log, blockchain, risk_assessment, transaction  # noqa: F401
from app.services.blockchain import backfill_blockchain_evidence, validate_blockchain
from app.services.seed import seed_default_roles


def main() -> int:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema_compatibility()
    seed_default_roles()
    with SessionLocal() as db:
        result = backfill_blockchain_evidence(db)
        validation = validate_blockchain(db)
        db.commit()
    print(json.dumps({"backfill": result, "validation": validation}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
