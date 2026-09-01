from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "final-e2e-secret"

from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app
from app.services.seed import seed_default_roles


REPORT_PATH = ROOT / "reports" / "final" / "e2e_results.json"


def register(client: TestClient, email: str, role: str = "CLIENT") -> dict:
    payload = {
        "first_name": email.split("@")[0].split("-")[0].title(),
        "last_name": "Demo",
        "email": email,
        "phone": "55551234",
        "country": "Guatemala",
        "password": "Password123",
        "confirm_password": "Password123",
        "terms_accepted": True,
        "human_check_accepted": True,
        "document_type": "DPI",
        "fictitious_document_id": "1234567890123",
        "birth_date": "1995-05-15",
        "occupation": "Demo",
        "role": role,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"})
    assert token.status_code == 200, token.text
    return {"user": response.json(), "headers": {"Authorization": f"Bearer {token.json()['access_token']}"}}


def add_beneficiary(client: TestClient, headers: dict) -> dict:
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json={
            "first_name": "Javier",
            "last_name": "Guzman",
            "email": "javier.receiver@example.com",
            "relationship": "Familia",
            "country": "Guatemala",
            "currency": "GTQ",
            "department": "Guatemala",
            "municipality": "Guatemala",
            "delivery_method": "BANK_DEPOSIT",
            "bank_name": "Banco Industrial, S.A.",
            "account_type": "Ahorro",
            "account_last_four": "1234",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_remittance(client: TestClient, headers: dict, beneficiary_id: int) -> dict:
    from app.services import remittances

    remittances.get_banguat_usd_gtq_rate = lambda: None
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "beneficiary_id": beneficiary_id,
            "origin_country": "Estados Unidos",
            "destination_country": "Guatemala",
            "amount": "300.00",
            "currency": "USD",
            "payment_method": "BANK_TRANSFER",
            "delivery_method": "BANK_DEPOSIT",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def record(results: list[dict], name: str, response, expected: int) -> None:
    results.append({"name": name, "status_code": response.status_code, "expected": expected, "passed": response.status_code == expected})


def main() -> int:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_default_roles()
    results: list[dict] = []
    with TestClient(app) as client:
        client_user = register(client, "client.final@example.com")
        risk_user = register(client, "risk.final@example.com", "RISK_ANALYST")
        admin_user = register(client, "admin.final@example.com", "ADMIN")
        beneficiary = add_beneficiary(client, client_user["headers"])
        remittance = add_remittance(client, client_user["headers"], beneficiary["id"])

        record(results, "CLIENT read own transactions", client.get("/api/v1/transactions", headers=client_user["headers"]), 200)
        record(results, "CLIENT read tracking", client.get(f"/api/v1/tracking/{remittance['remittance_number']}", headers=client_user["headers"]), 200)
        record(results, "CLIENT blockchain own evidence", client.get(f"/api/v1/blockchain/verify/{remittance['id']}", headers=client_user["headers"]), 200)
        record(results, "CLIENT assistant own status", client.post("/api/v1/assistant/chat", headers=client_user["headers"], json={"message": "Estado de mi ultima remesa"}), 200)
        record(results, "CLIENT BI denied", client.get("/api/v1/bi/overview", headers=client_user["headers"]), 403)
        record(results, "CLIENT risk denied", client.get("/api/v1/risk/dashboard", headers=client_user["headers"]), 403)
        record(results, "RISK dashboard", client.get("/api/v1/risk/dashboard", headers=risk_user["headers"]), 200)
        record(results, "RISK forecast", client.get("/api/v1/forecasting/summary", headers=risk_user["headers"]), 200)
        record(results, "RISK assistant", client.post("/api/v1/assistant/chat", headers=risk_user["headers"], json={"message": "Resume la cola de riesgo"}), 200)
        record(results, "ADMIN system info", client.get("/api/v1/system/info", headers=admin_user["headers"]), 200)
        record(results, "ADMIN BI overview", client.get("/api/v1/bi/overview", headers=admin_user["headers"]), 200)
        record(results, "ADMIN blockchain validate", client.get("/api/v1/blockchain/validate", headers=admin_user["headers"]), 200)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "total": len(results),
        "passed": sum(item["passed"] for item in results),
        "failed": len([item for item in results if not item["passed"]]),
        "results": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
