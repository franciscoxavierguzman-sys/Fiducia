from decimal import Decimal
from pathlib import Path

from app.analytics.pipeline import run_pipeline, transform_records
from app.analytics.synthetic import generate_synthetic_records
from app.analytics.validation import validate_records
from app.core.config import settings


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "Ana",
        "last_name": "Analitica",
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
        "role": role,
    }
    user = client.post("/api/v1/auth/register", json=payload).json()
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123"},
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def create_operational_remittance(client, headers):
    beneficiary = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json={
            "first_name": "Javier",
            "last_name": "Guzman",
            "email": "receiver.phase3@example.com",
            "relationship": "Amigo / Amiga",
            "country": "Guatemala",
            "currency": "GTQ",
            "department": "Guatemala",
            "municipality": "Guatemala",
            "delivery_method": "BANK_DEPOSIT",
            "account_type": "Ahorro",
            "account_last_four": "1234",
        },
    )
    assert beneficiary.status_code == 201
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "beneficiary_id": beneficiary.json()["id"],
            "origin_country": "Estados Unidos",
            "destination_country": "Guatemala",
            "amount": "400.00",
            "currency": "USD",
            "payment_method": "BANK_TRANSFER",
            "delivery_method": "BANK_DEPOSIT",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_synthetic_generation_is_reproducible_and_valid():
    first = generate_synthetic_records(records=250, seed=7, fraud_rate=Decimal("0.04"))
    second = generate_synthetic_records(records=250, seed=7, fraud_rate=Decimal("0.04"))

    assert first == second
    assert len(first) == 250
    assert any(row["fraud_label"] == "1" for row in first)
    assert all(row["origin_country"] != row["destination_country"] for row in first)

    report = validate_records(first)
    assert report["valid"] is True
    assert report["error_count"] == 0


def test_validation_detects_financial_and_identity_errors():
    rows = generate_synthetic_records(records=5, seed=9)
    rows[0]["destination_country"] = rows[0]["origin_country"]
    rows[1]["commission_amount"] = "0.00"
    rows[2]["exchange_rate"] = "-1"
    rows[3]["source_currency"] = "XXX"
    rows[4]["remittance_id"] = rows[3]["remittance_id"]

    report = validate_records(rows)
    assert report["valid"] is False
    assert report["error_count"] >= 5


def test_pipeline_exports_processed_dataset(tmp_path: Path):
    synthetic_path = tmp_path / "synthetic.csv"
    processed_path = tmp_path / "processed.csv"
    report_path = tmp_path / "report.json"

    report = run_pipeline(
        records=120,
        seed=11,
        synthetic_path=synthetic_path,
        processed_path=processed_path,
        report_path=report_path,
    )

    assert report["valid"] is True
    assert report["record_count"] == 120
    assert synthetic_path.exists()
    assert processed_path.exists()
    assert report_path.exists()
    assert "amount_bucket" in processed_path.read_text(encoding="utf-8").splitlines()[0]
    assert "risk_band_experimental" in processed_path.read_text(encoding="utf-8").splitlines()[0]


def test_transform_records_preserves_decimal_financial_math():
    row = generate_synthetic_records(records=1, seed=13)[0]
    transformed = transform_records([row])[0]
    source_amount = Decimal(transformed["source_amount"])
    commission_rate = Decimal(transformed["commission_rate"])
    commission_amount = Decimal(transformed["commission_amount"])
    total_debit_amount = Decimal(transformed["total_debit_amount"])

    assert commission_amount == (source_amount * commission_rate).quantize(Decimal("0.01"))
    assert total_debit_amount == source_amount + commission_amount
    assert transformed["amount_bucket"]
    assert transformed["risk_band_experimental"] in {"BAJO", "MEDIO", "ALTO"}


def test_analytics_endpoints_require_authorized_role(client):
    _, client_headers = register_and_login(client, "client-analytics@example.com")
    _, admin_headers = register_and_login(client, "admin-analytics@example.com", role="ADMIN")
    create_operational_remittance(client, admin_headers)

    forbidden = client.get("/api/v1/analytics/summary", headers=client_headers)
    assert forbidden.status_code == 403

    summary = client.get("/api/v1/analytics/summary", headers=admin_headers)
    assert summary.status_code == 200
    body = summary.json()
    assert body["total_remittances"] == 1
    assert Decimal(body["volume_usd_equivalent"]) == Decimal("400.00")
    assert body["top_corridor"] == "Estados Unidos -> Guatemala"

    over_time = client.get("/api/v1/analytics/remittances-over-time", headers=admin_headers)
    assert over_time.status_code == 200
    assert over_time.json()[0]["count"] == 1

    statuses = client.get("/api/v1/analytics/status-distribution", headers=admin_headers)
    assert statuses.status_code == 200
    assert statuses.json()[0]["label"] == "AVAILABLE"

    methods = client.get("/api/v1/analytics/method-distribution", headers=admin_headers)
    assert methods.status_code == 200
    assert methods.json()["funding_methods"][0]["label"] == "BANK_TRANSFER"


def test_phase1_and_phase2_regression_still_allows_client_flow(client):
    user, headers = register_and_login(client, "phase3-regression@example.com")
    transaction = create_operational_remittance(client, headers)

    me = client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == user["id"]

    detail = client.get(f"/api/v1/transactions/{transaction['id']}", headers=headers)
    assert detail.status_code == 200
    assert Decimal(detail.json()["commission_amount"]) == Decimal("9.00")
    assert Decimal(detail.json()["destination_amount"]) == Decimal("3120.00")
    assert Decimal(str(settings.commission_rate)) == Decimal("0.0225")
