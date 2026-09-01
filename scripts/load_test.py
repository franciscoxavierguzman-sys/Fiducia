from __future__ import annotations

import json
import os
import statistics
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

LOAD_TEST_DB = Path(tempfile.gettempdir()) / "fiducia_load_test.sqlite"
os.environ["DATABASE_URL"] = f"sqlite:///{LOAD_TEST_DB.as_posix()}"
os.environ["SECRET_KEY"] = "load-test-secret"

from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app
from app.services.seed import seed_default_roles


REPORT_PATH = ROOT / "reports" / "final" / "load_test_results.json"


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(len(ordered) * ratio) - 1))
    return round(ordered[index], 2)


def request_once(client: TestClient, method: str, path: str, headers: dict | None = None, json_body: dict | None = None) -> dict:
    started = time.perf_counter()
    response = client.request(method, path, headers=headers, json=json_body)
    return {"status_code": response.status_code, "duration_ms": (time.perf_counter() - started) * 1000}


def run_scenario(client: TestClient, name: str, concurrency: int, requests: int, method: str, path: str, headers: dict | None = None, json_body: dict | None = None) -> dict:
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(request_once, client, method, path, headers, json_body) for _ in range(requests)]
        results = [future.result() for future in as_completed(futures)]
    durations = [item["duration_ms"] for item in results]
    errors = len([item for item in results if item["status_code"] >= 400])
    return {
        "scenario": name,
        "concurrency": concurrency,
        "requests": requests,
        "errors": errors,
        "p50_ms": percentile(durations, 0.50),
        "p95_ms": percentile(durations, 0.95),
        "max_ms": round(max(durations), 2) if durations else 0,
        "average_ms": round(statistics.mean(durations), 2) if durations else 0,
    }


def login(headers_email: str, role: str = "CLIENT") -> dict:
    with TestClient(app) as client:
        payload = {
            "first_name": "Load",
            "last_name": role.title(),
            "email": headers_email,
            "phone": "55551234",
            "country": "Guatemala",
            "password": "Password123",
            "confirm_password": "Password123",
            "terms_accepted": True,
            "human_check_accepted": True,
            "document_type": "DPI",
            "fictitious_document_id": "1234567890123",
            "birth_date": "1995-05-15",
            "role": role,
        }
        client.post("/api/v1/auth/register", json=payload)
        token = client.post("/api/v1/auth/login", json={"email": headers_email, "password": "Password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def main() -> int:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_roles()
    client_headers = login("load-client@example.com")
    admin_headers = login("load-admin@example.com", "ADMIN")
    scenarios = []
    with TestClient(app) as client:
        for concurrency in (10, 25, 50):
            scenarios.append(run_scenario(client, "read-heavy-health", concurrency, concurrency * 2, "GET", "/health"))
            scenarios.append(run_scenario(client, "remittance-read", concurrency, concurrency * 2, "GET", "/api/v1/transactions", client_headers))
            scenarios.append(run_scenario(client, "bi-read", concurrency, concurrency * 2, "GET", "/api/v1/bi/overview", admin_headers))
            scenarios.append(
                run_scenario(
                    client,
                    "assistant-deterministic",
                    concurrency,
                    concurrency * 2,
                    "POST",
                    "/api/v1/assistant/chat",
                    client_headers,
                    {"message": "Como agrego un beneficiario?"},
                )
            )
    payload = {"generated_at": datetime.now(UTC).isoformat(), "results": scenarios}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if all(item["errors"] == 0 for item in scenarios) else 1


if __name__ == "__main__":
    raise SystemExit(main())
