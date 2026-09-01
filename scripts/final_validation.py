from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

VALIDATION_DB = Path(tempfile.gettempdir()) / "fiducia_final_validation.sqlite"
os.environ["DATABASE_URL"] = f"sqlite:///{VALIDATION_DB.as_posix()}"
os.environ.setdefault("SECRET_KEY", "final-validation-secret")

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.version import APP_VERSION
from app.main import app
from app.services.assistant import assistant_info
from app.services.blockchain import blockchain_info
from app.services.forecasting import get_forecast_model_info
from app.services.ml_risk import get_model_info
from app.services.risk_engine import risk_engine_info


REPORT_DIR = ROOT / "reports" / "final"
MODEL_FILES = [
    ROOT / "ml" / "artifacts" / "fraud_model.joblib",
    ROOT / "ml" / "artifacts" / "model_metadata.json",
    ROOT / "ml" / "artifacts" / "model_metrics.json",
    ROOT / "ml" / "artifacts" / "anomaly_model.joblib",
    ROOT / "ml" / "artifacts" / "anomaly_metadata.json",
    ROOT / "ml" / "artifacts" / "risk_engine_metadata.json",
    ROOT / "ml" / "artifacts" / "forecasting" / "forecast_metadata.json",
    ROOT / "ml" / "artifacts" / "forecasting" / "forecast_metrics.json",
]
DATASET_FILES = [
    ROOT / "data" / "processed" / "remittances_analytics.csv",
    ROOT / "data" / "processed" / "forecasting" / "weekly_remittances_forecasting.csv",
]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def collect_checksums(paths: list[Path]) -> dict:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): {
            "exists": path.exists(),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        for path in paths
    }


def main() -> int:
    generated_at = datetime.now(UTC).isoformat()
    model_checksums = {"generated_at": generated_at, "files": collect_checksums(MODEL_FILES)}
    dataset_checksums = {"generated_at": generated_at, "files": collect_checksums(DATASET_FILES)}
    write_json(REPORT_DIR / "model-artifact-checksums.json", model_checksums)
    write_json(REPORT_DIR / "dataset-checksums.json", dataset_checksums)

    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")

    validation = {
        "generated_at": generated_at,
        "app_version": APP_VERSION,
        "environment": settings.environment,
        "database_type": settings.database_url.split(":", 1)[0],
        "health": {"status_code": health.status_code, "body": health.json()},
        "ready": {"status_code": ready.status_code, "body": ready.json()},
        "ml": get_model_info().model_dump(),
        "risk_engine": risk_engine_info(),
        "forecast": get_forecast_model_info(),
        "assistant": assistant_info(),
        "blockchain": "checked_by_service",
    }
    try:
        from app.db.session import SessionLocal

        with SessionLocal() as db:
            validation["blockchain"] = blockchain_info(db)
    except Exception as exc:
        validation["blockchain"] = {"available": False, "message": str(exc)}

    write_json(REPORT_DIR / "final_validation.json", validation)
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    return 0 if health.status_code == 200 and ready.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
