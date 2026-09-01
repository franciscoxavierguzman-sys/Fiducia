from decimal import Decimal

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.transaction import Transaction


def register_and_login(client, email: str):
    payload = {
        "first_name": "Test",
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
    }
    user = client.post("/api/v1/auth/register", json=payload).json()
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123"},
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def beneficiary_payload(**overrides):
    payload = {
        "first_name": "Rosa",
        "last_name": "Lopez",
        "relationship": "Madre",
        "country": "Guatemala",
        "currency": "GTQ",
        "department": "Guatemala",
        "municipality": "Guatemala",
        "delivery_method": "BANK_DEPOSIT",
        "bank_name": "Banco Simulado",
        "account_type": "Ahorro",
        "account_last_four": "1234",
    }
    payload.update(overrides)
    return payload


def create_beneficiary(client, headers, **overrides):
    response = client.post("/api/v1/beneficiaries", headers=headers, json=beneficiary_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def simulation_payload(beneficiary_id: int, **overrides):
    payload = {
        "beneficiary_id": beneficiary_id,
        "origin_country": "Estados Unidos",
        "destination_country": "Guatemala",
        "amount": "400.00",
        "currency": "USD",
        "payment_method": "BANK_TRANSFER",
        "delivery_method": "BANK_DEPOSIT",
    }
    payload.update(overrides)
    return payload


def test_beneficiary_crud_and_ownership(client):
    _, owner_headers = register_and_login(client, "owner@example.com")
    _, other_headers = register_and_login(client, "other@example.com")

    beneficiary = create_beneficiary(client, owner_headers)
    assert beneficiary["account_last_four"] == "1234"

    list_response = client.get("/api/v1/beneficiaries", headers=owner_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/api/v1/beneficiaries/{beneficiary['id']}", headers=owner_headers)
    assert detail_response.status_code == 200

    update_response = client.patch(
        f"/api/v1/beneficiaries/{beneficiary['id']}",
        headers=owner_headers,
        json={"municipality": "Mixco"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["municipality"] == "Mixco"

    forbidden_detail = client.get(f"/api/v1/beneficiaries/{beneficiary['id']}", headers=other_headers)
    assert forbidden_detail.status_code == 404

    forbidden_update = client.patch(
        f"/api/v1/beneficiaries/{beneficiary['id']}",
        headers=other_headers,
        json={"municipality": "Villa Nueva"},
    )
    assert forbidden_update.status_code == 404


def test_beneficiary_rejects_invalid_last_four(client):
    _, headers = register_and_login(client, "invalidlastfour@example.com")
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json=beneficiary_payload(account_last_four="12A4"),
    )
    assert response.status_code == 422


def test_beneficiary_allows_foreign_city_without_guatemala_location(client):
    _, headers = register_and_login(client, "foreigncity@example.com")
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json=beneficiary_payload(
            country="Estados Unidos",
            currency="USD",
            city="New York",
            department="",
            municipality="",
            delivery_method="TRANSFER",
            bank_name="Banco US",
            account_last_four="4225",
        ),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["country"] == "Estados Unidos"
    assert body["city"] == "New York"
    assert body["department"] == "N/A"
    assert body["municipality"] == "N/A"


def test_simulation_calculates_commission_total_and_destination(client):
    _, headers = register_and_login(client, "simulate@example.com")
    beneficiary = create_beneficiary(client, headers)

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"]),
    )
    assert response.status_code == 200
    body = response.json()
    assert Decimal(body["commission_rate"]) == Decimal("0.022500")
    assert Decimal(body["commission_amount"]) == Decimal("9.00")
    assert Decimal(body["total_amount"]) == Decimal("409.00")
    assert Decimal(body["exchange_rate"]) == Decimal("7.800000")
    assert Decimal(body["destination_amount"]) == Decimal("3120.00")


def test_simulation_validations(client):
    _, headers = register_and_login(client, "validations@example.com")
    beneficiary = create_beneficiary(client, headers)

    invalid_amount = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], amount="0.00"),
    )
    assert invalid_amount.status_code == 422

    out_of_range = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], amount=str(settings.maximum_remittance_amount + 1)),
    )
    assert out_of_range.status_code == 400
    assert out_of_range.json()["detail"]["code"] == "AMOUNT_OUT_OF_RANGE"

    invalid_beneficiary = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(9999),
    )
    assert invalid_beneficiary.status_code == 404

    invalid_country = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], origin_country="Francia"),
    )
    assert invalid_country.status_code == 400
    assert invalid_country.json()["detail"]["code"] == "INVALID_COUNTRY"

    invalid_currency = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], currency="EUR"),
    )
    assert invalid_currency.status_code == 400
    assert invalid_currency.json()["detail"]["code"] == "INVALID_CURRENCY"


def test_transaction_creation_history_detail_and_ownership(client):
    _, owner_headers = register_and_login(client, "txowner@example.com")
    _, other_headers = register_and_login(client, "txother@example.com")
    beneficiary = create_beneficiary(client, owner_headers)

    unauthenticated = client.post("/api/v1/transactions", json=simulation_payload(beneficiary["id"]))
    assert unauthenticated.status_code == 401

    created_response = client.post(
        "/api/v1/transactions",
        headers=owner_headers,
        json=simulation_payload(beneficiary["id"]),
    )
    assert created_response.status_code == 201
    transaction = created_response.json()
    assert transaction["transaction_id"].startswith("FID-")
    assert transaction["status"] == "AVAILABLE"
    assert Decimal(transaction["commission_amount"]) == Decimal("9.00")
    assert Decimal(transaction["destination_amount"]) == Decimal("3120.00")
    assert transaction["rule_score"] is not None
    assert transaction["ml_probability"] is not None
    assert transaction["final_risk_score"] is not None

    history_response = client.get("/api/v1/transactions", headers=owner_headers)
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1

    detail_response = client.get(f"/api/v1/transactions/{transaction['id']}", headers=owner_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["beneficiary"]["first_name"] == "Rosa"

    other_detail = client.get(f"/api/v1/transactions/{transaction['id']}", headers=other_headers)
    assert other_detail.status_code == 404


def test_transaction_rejects_beneficiary_from_another_user(client):
    _, owner_headers = register_and_login(client, "beneficiaryowner@example.com")
    _, other_headers = register_and_login(client, "beneficiaryother@example.com")
    beneficiary = create_beneficiary(client, owner_headers)

    response = client.post(
        "/api/v1/transactions",
        headers=other_headers,
        json=simulation_payload(beneficiary["id"]),
    )
    assert response.status_code == 404


def test_transaction_persists_historical_values(client):
    _, headers = register_and_login(client, "persist@example.com")
    beneficiary = create_beneficiary(client, headers)

    created_response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json=simulation_payload(beneficiary["id"]),
    )
    assert created_response.status_code == 201
    transaction = created_response.json()

    original_rate = settings.commission_rate
    try:
        settings.commission_rate = 0.05
        detail_response = client.get(f"/api/v1/transactions/{transaction['id']}", headers=headers)
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert Decimal(detail["commission_rate"]) == Decimal("0.022500")
        assert Decimal(detail["exchange_rate"]) == Decimal("7.800000")
        assert Decimal(detail["commission_amount"]) == Decimal("9.00")
        assert Decimal(detail["destination_amount"]) == Decimal("3120.00")
    finally:
        settings.commission_rate = original_rate


def test_inbound_corridor_united_states_to_guatemala(client):
    _, headers = register_and_login(client, "inbound@example.com")
    beneficiary = create_beneficiary(client, headers, country="Guatemala", currency="GTQ")

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], origin_country="Estados Unidos", destination_country="Guatemala", currency="USD"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_currency"] == "USD"
    assert body["destination_currency"] == "GTQ"
    assert Decimal(body["commission_amount"]) == Decimal("9.00")
    assert Decimal(body["destination_amount"]) == Decimal("3120.00")


def test_inbound_corridor_uses_banguat_rate_for_guatemala_destination(client, monkeypatch):
    import app.services.remittances as remittance_service

    monkeypatch.setattr(remittance_service, "get_banguat_usd_gtq_rate", lambda: Decimal("7.62422"))
    _, headers = register_and_login(client, "banguat@example.com")
    beneficiary = create_beneficiary(client, headers, country="Guatemala", currency="GTQ")

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(beneficiary["id"], origin_country="Estados Unidos", destination_country="Guatemala", currency="USD"),
    )
    assert response.status_code == 200
    body = response.json()
    assert Decimal(body["exchange_rate"]) == Decimal("7.624220")
    assert Decimal(body["destination_amount"]) == Decimal("3049.69")
    assert body["exchange_rate_source"] == "Banco de Guatemala"
    assert body["is_exchange_rate_simulated"] is False


def test_inbound_corridor_allows_gtq_funding_source_with_usd_amount(client):
    _, headers = register_and_login(client, "gtqfunding@example.com")
    beneficiary = create_beneficiary(client, headers, country="Guatemala", currency="GTQ")
    funding = client.post(
        "/api/v1/funding-sources",
        headers=headers,
        json={
            "type": "BANK_ACCOUNT",
            "display_name": "Cuenta GTQ",
            "provider": "Banco Industrial, S.A.",
            "last_four": "7291",
            "account_type": "Ahorro",
            "account_number": "1234567291",
            "currency": "GTQ",
        },
    )
    assert funding.status_code == 201

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(
            beneficiary["id"],
            origin_country="Estados Unidos",
            destination_country="Guatemala",
            amount="400.00",
            currency="USD",
            funding_source_id=funding.json()["id"],
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_currency"] == "USD"
    assert body["total_debit_currency"] == "GTQ"
    assert Decimal(body["total_debit_amount"]) == Decimal("3190.20")
    assert Decimal(body["destination_amount"]) == Decimal("3120.00")


def test_outbound_corridor_guatemala_to_united_states(client):
    _, headers = register_and_login(client, "outbound@example.com")
    beneficiary = create_beneficiary(
        client,
        headers,
        first_name="John",
        last_name="Smith",
        country="Estados Unidos",
        currency="USD",
        city="Los Angeles",
    )

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(
            beneficiary["id"],
            origin_country="Guatemala",
            destination_country="Estados Unidos",
            amount="3000.00",
            currency="GTQ",
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_currency"] == "GTQ"
    assert body["destination_currency"] == "USD"
    assert Decimal(body["commission_amount"]) == Decimal("67.50")
    assert Decimal(body["total_amount"]) == Decimal("3067.50")
    assert Decimal(body["exchange_rate"]) == Decimal("0.128205")
    assert Decimal(body["destination_amount"]) == Decimal("384.62")


def test_rejects_non_guatemala_corridor_and_same_country(client):
    _, headers = register_and_login(client, "corridors@example.com")
    beneficiary = create_beneficiary(client, headers, country="Canada", currency="CAD", city="Toronto")

    unsupported = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(
            beneficiary["id"],
            origin_country="Estados Unidos",
            destination_country="Canada",
            currency="USD",
        ),
    )
    assert unsupported.status_code == 400
    assert unsupported.json()["detail"]["code"] == "UNSUPPORTED_CORRIDOR"

    same_country = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(
            beneficiary["id"],
            origin_country="Guatemala",
            destination_country="Guatemala",
            currency="GTQ",
        ),
    )
    assert same_country.status_code == 400
    assert same_country.json()["detail"]["code"] == "SAME_COUNTRY_CORRIDOR"


def test_rejects_incompatible_beneficiary_country(client):
    _, headers = register_and_login(client, "incompatible@example.com")
    guatemala_beneficiary = create_beneficiary(client, headers, country="Guatemala", currency="GTQ")

    response = client.post(
        "/api/v1/remittances/simulate",
        headers=headers,
        json=simulation_payload(
            guatemala_beneficiary["id"],
            origin_country="Guatemala",
            destination_country="Estados Unidos",
            amount="3000.00",
            currency="GTQ",
        ),
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INCOMPATIBLE_BENEFICIARY"


def test_registered_beneficiary_can_view_received_remittance(client):
    _, sender_headers = register_and_login(client, "receive-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "receive-beneficiary@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email=receiver["email"])

    created_response = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    )
    assert created_response.status_code == 201
    transaction = created_response.json()
    assert transaction["beneficiary_user_id"] == receiver["id"]

    received_response = client.get("/api/v1/transactions/received", headers=receiver_headers)
    assert received_response.status_code == 200
    received = received_response.json()
    assert len(received) == 1
    assert received[0]["id"] == transaction["id"]
    assert received[0]["sender"]["email"] == "receive-sender@example.com"


def test_other_user_cannot_access_received_remittance(client):
    _, sender_headers = register_and_login(client, "secure-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "secure-beneficiary@example.com")
    _, other_headers = register_and_login(client, "secure-other@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email=receiver["email"])

    transaction = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    ).json()

    allowed = client.get(f"/api/v1/transactions/{transaction['id']}", headers=receiver_headers)
    assert allowed.status_code == 200

    forbidden = client.get(f"/api/v1/transactions/{transaction['id']}", headers=other_headers)
    assert forbidden.status_code == 404

    forbidden_receive = client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=other_headers)
    assert forbidden_receive.status_code == 404


def test_cannot_receive_remittance_with_non_available_status(client):
    _, sender_headers = register_and_login(client, "state-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "state-beneficiary@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email=receiver["email"])
    transaction = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    ).json()

    with SessionLocal() as db:
        saved = db.get(Transaction, transaction["id"])
        saved.status = "PROCESSING"
        db.commit()

    response = client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=receiver_headers)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_TRANSACTION_STATUS"


def test_available_remittance_can_be_completed_once_and_audited(client):
    _, sender_headers = register_and_login(client, "complete-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "complete-beneficiary@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email=receiver["email"])
    transaction = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    ).json()

    response = client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=receiver_headers)
    assert response.status_code == 200
    completed = response.json()
    assert completed["status"] == "COMPLETED"

    second_response = client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=receiver_headers)
    assert second_response.status_code == 400
    assert second_response.json()["detail"]["code"] == "INVALID_TRANSACTION_STATUS"

    sender_detail = client.get(f"/api/v1/transactions/{transaction['id']}", headers=sender_headers)
    assert sender_detail.status_code == 200
    assert sender_detail.json()["status"] == "COMPLETED"

    with SessionLocal() as db:
        audit = db.query(AuditLog).filter(AuditLog.action == "REMITTANCE_COMPLETED").one()
        assert audit.user_id == receiver["id"]
        assert audit.entity_id == completed["transaction_id"]
        assert audit.metadata_json["previous_status"] == "AVAILABLE"
        assert audit.metadata_json["new_status"] == "COMPLETED"


def test_unregistered_beneficiary_does_not_see_received_remittance_until_linked(client):
    _, sender_headers = register_and_login(client, "later-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "later-beneficiary@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email="pending-link@example.com")

    created = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    ).json()
    assert created["beneficiary_user_id"] is None

    empty_received = client.get("/api/v1/transactions/received", headers=receiver_headers)
    assert empty_received.status_code == 200
    assert empty_received.json() == []

    linked = client.patch(
        f"/api/v1/beneficiaries/{beneficiary['id']}",
        headers=sender_headers,
        json={"email": receiver["email"]},
    )
    assert linked.status_code == 200
    assert linked.json()["beneficiary_user_id"] == receiver["id"]

    received_response = client.get("/api/v1/transactions/received", headers=receiver_headers)
    assert received_response.status_code == 200
    assert received_response.json()[0]["id"] == created["id"]


def test_received_remittance_links_automatically_by_beneficiary_email(client):
    _, sender_headers = register_and_login(client, "auto-link-sender@example.com")
    beneficiary = create_beneficiary(client, sender_headers, email="auto-link-receiver@example.com")

    created = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json=simulation_payload(beneficiary["id"]),
    ).json()
    assert created["beneficiary_user_id"] is None

    receiver, receiver_headers = register_and_login(client, "auto-link-receiver@example.com")
    received_response = client.get("/api/v1/transactions/received", headers=receiver_headers)
    assert received_response.status_code == 200
    received = received_response.json()
    assert len(received) == 1
    assert received[0]["id"] == created["id"]
    assert received[0]["beneficiary_user_id"] == receiver["id"]

    receive_response = client.post(f"/api/v1/transactions/{created['id']}/receive", headers=receiver_headers)
    assert receive_response.status_code == 200
    assert receive_response.json()["status"] == "COMPLETED"
