from datetime import datetime
from decimal import Decimal

from app.bi.calculations import calculate_overview
from app.bi.filters import BIFilters
from app.db.session import SessionLocal
from app.models.beneficiary import Beneficiary
from app.models.risk_assessment import RiskAssessment
from app.models.role import Role
from app.models.transaction import Transaction
from app.models.user import User
from app.security.passwords import hash_password


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "BI",
        "last_name": "User",
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
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"}).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def seed_bi_dataset():
    with SessionLocal() as db:
        client_role = db.query(Role).filter(Role.name == "CLIENT").one()
        sender_one = User(
            role_id=client_role.id,
            first_name="Ana",
            last_name="Lopez",
            email="ana-bi@example.com",
            phone="1111",
            country="Guatemala",
            password_hash=hash_password("Password123"),
        )
        sender_two = User(
            role_id=client_role.id,
            first_name="Carlos",
            last_name="Diaz",
            email="carlos-bi@example.com",
            phone="2222",
            country="Guatemala",
            password_hash=hash_password("Password123"),
        )
        db.add_all([sender_one, sender_two])
        db.flush()
        beneficiary = Beneficiary(
            sender_id=sender_one.id,
            first_name="Rosa",
            last_name="Lopez",
            relationship="Madre",
            country="Guatemala",
            currency="GTQ",
            department="Guatemala",
            municipality="Guatemala",
            delivery_method="BANK_DEPOSIT",
            account_last_four="1234",
        )
        db.add(beneficiary)
        db.flush()
        transactions = [
            _tx(sender_one.id, beneficiary.id, "2026-07-01T10:00:00", "USD", "Estados Unidos", "Guatemala", "COMPLETED", "100.00", "2.25"),
            _tx(sender_one.id, beneficiary.id, "2026-07-08T10:00:00", "GTQ", "Guatemala", "Estados Unidos", "AVAILABLE", "780.00", "17.55"),
            _tx(sender_two.id, beneficiary.id, "2026-07-15T10:00:00", "USD", "Estados Unidos", "Guatemala", "REVIEW_REQUIRED", "300.00", "6.75"),
            _tx(sender_two.id, beneficiary.id, "2026-06-20T10:00:00", "USD", "Estados Unidos", "Guatemala", "COMPLETED", "50.00", "1.13"),
            _tx(sender_one.id, beneficiary.id, "2026-06-25T10:00:00", "USD", "Estados Unidos", "Mexico", "REJECTED", "200.00", "4.50"),
        ]
        db.add_all(transactions)
        db.flush()
        db.add_all(
            [
                RiskAssessment(
                    remittance_id=transactions[0].id,
                    final_risk_score=Decimal("12.00"),
                    risk_band="LOW",
                    recommended_action="CONTINUE",
                    risk_engine_version="risk-engine-v1.1",
                    review_status="PENDING",
                ),
                RiskAssessment(
                    remittance_id=transactions[2].id,
                    final_risk_score=Decimal("44.00"),
                    risk_band="HIGH",
                    recommended_action="MANUAL_REVIEW",
                    risk_engine_version="risk-engine-v1.1",
                    review_status="REVIEWED",
                    review_decision="ESCALATE",
                ),
            ]
        )
        db.commit()


def _tx(sender_id, beneficiary_id, created_at, currency, origin, destination, status, source_amount, commission):
    amount = Decimal(source_amount)
    return Transaction(
        sender_id=sender_id,
        beneficiary_id=beneficiary_id,
        origin_country=origin,
        destination_country=destination,
        source_amount=amount,
        source_currency=currency,
        destination_currency="GTQ" if destination == "Guatemala" else "USD",
        amount=amount,
        currency=currency,
        exchange_rate=Decimal("7.800000") if currency == "USD" else Decimal("0.128205"),
        commission_rate=Decimal("0.022500"),
        commission_amount=Decimal(commission),
        total_amount=amount + Decimal(commission),
        destination_amount=amount,
        payment_method="BANK_TRANSFER",
        delivery_method="BANK_DEPOSIT",
        status=status,
        created_at=datetime.fromisoformat(created_at),
    )


def test_bi_kpi_formulas_use_usd_equivalent_and_historical_commissions(client):
    seed_bi_dataset()
    with SessionLocal() as db:
        result = calculate_overview(db, BIFilters(date_from=datetime(2026, 7, 1), date_to=datetime(2026, 7, 31)))

    assert result["total_remittances"] == 3
    assert result["total_amount_usd_equivalent"] == Decimal("500.00")
    assert result["average_ticket_usd_equivalent"] == Decimal("166.67")
    assert result["total_commission_revenue_usd_equivalent"] == Decimal("11.25")
    assert result["average_commission_usd_equivalent"] == Decimal("3.75")
    assert result["active_clients"] == 2
    assert result["active_corridors"] == 2
    assert result["completion_rate"] == Decimal("0.3333")


def test_bi_filters_period_comparison_zero_denominator_and_corridors(client):
    seed_bi_dataset()
    _, admin_headers = register_and_login(client, "admin-bi@example.com", role="ADMIN")

    overview = client.get(
        "/api/v1/bi/overview?date_from=2026-07-01T00:00:00&date_to=2026-07-31T23:59:59&origin_country=Estados Unidos",
        headers=admin_headers,
    )
    assert overview.status_code == 200
    body = overview.json()
    assert body["current"]["total_remittances"] == 2
    assert body["previous"]["total_remittances"] == 2
    assert body["changes"]["total_remittances"]["percentage_change"] == "0.0000"

    empty = client.get("/api/v1/bi/overview?status=DOES_NOT_EXIST", headers=admin_headers)
    assert empty.status_code == 200
    assert empty.json()["current"]["average_ticket_usd_equivalent"] is None

    corridors = client.get("/api/v1/bi/corridors?date_from=2026-07-01T00:00:00&date_to=2026-07-31T23:59:59", headers=admin_headers)
    assert corridors.status_code == 200
    assert corridors.json()[0]["commission_revenue_usd_equivalent"] == "9.00"


def test_bi_customers_operations_risk_forecast_insights_and_exports(client):
    seed_bi_dataset()
    _, analyst_headers = register_and_login(client, "analyst-bi@example.com", role="RISK_ANALYST")

    customers = client.get("/api/v1/bi/customers?date_from=2026-07-01T00:00:00&date_to=2026-07-31T23:59:59", headers=analyst_headers)
    assert customers.status_code == 200
    assert customers.json()["active_clients"] == 2
    assert customers.json()["returning_clients"] == 2
    assert customers.json()["repeat_sender_rate"] == "0.5000"

    operations = client.get("/api/v1/bi/operations", headers=analyst_headers)
    assert operations.status_code == 200
    assert operations.json()["review_required"] == 1

    risk = client.get("/api/v1/bi/risk", headers=analyst_headers)
    assert risk.status_code == 200
    assert risk.json()["assessment_count"] == 2
    assert risk.json()["escalated_reviews"] == 1

    forecast = client.get("/api/v1/bi/forecast", headers=analyst_headers)
    assert forecast.status_code == 200
    assert forecast.json()["model_version"] == "remittance-forecast-v1"

    summary = client.get("/api/v1/bi/executive-summary?date_from=2026-07-01T00:00:00&date_to=2026-07-31T23:59:59", headers=analyst_headers)
    assert summary.status_code == 200
    assert summary.json()["highlights"]

    csv_response = client.get("/api/v1/bi/exports/corridors.csv", headers=analyst_headers)
    assert csv_response.status_code == 200
    assert "corridor,remittance_count" in csv_response.text
    assert "ana-bi@example.com" not in csv_response.text


def test_bi_authorization_and_invalid_date_range(client):
    _, client_headers = register_and_login(client, "client-bi@example.com")
    _, admin_headers = register_and_login(client, "admin-range-bi@example.com", role="ADMIN")

    forbidden = client.get("/api/v1/bi/overview", headers=client_headers)
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "BI_FORBIDDEN"

    invalid = client.get("/api/v1/bi/overview?date_from=2026-08-01T00:00:00&date_to=2026-07-01T00:00:00", headers=admin_headers)
    assert invalid.status_code == 422
    assert invalid.json()["detail"]["code"] == "INVALID_DATE_RANGE"
