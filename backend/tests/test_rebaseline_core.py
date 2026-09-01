from decimal import Decimal


def register_and_login(client, email: str):
    payload = {
        "first_name": "Core",
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


def test_catalogs_are_available(client):
    _, headers = register_and_login(client, "catalogs@example.com")

    countries = client.get("/api/v1/catalogs/countries", headers=headers)
    assert countries.status_code == 200
    assert any(country["name"] == "Guatemala" and country["currency_code"] == "GTQ" for country in countries.json())

    relationships = client.get("/api/v1/catalogs/beneficiary-relationships", headers=headers)
    assert relationships.status_code == 200
    assert any(relationship["name"] == "Padre / Madre" for relationship in relationships.json())

    departments = client.get("/api/v1/catalogs/departments", headers=headers)
    assert departments.status_code == 200
    guatemala = next(item for item in departments.json() if item["name"] == "Guatemala")

    municipalities = client.get(f"/api/v1/catalogs/departments/{guatemala['id']}/municipalities", headers=headers)
    assert municipalities.status_code == 200
    assert any(item["name"] == "Mixco" for item in municipalities.json())


def test_profile_can_be_updated_without_role_changes(client):
    user, headers = register_and_login(client, "profile@example.com")

    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"phone": "55559999", "occupation": "Comerciante", "first_name": "Perfil"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Perfil"
    assert body["phone"] == "55559999"
    assert body["occupation"] == "Comerciante"
    assert body["role"]["name"] == "CLIENT"
    assert body["id"] == user["id"]


def test_funding_source_crud_default_and_ownership(client):
    _, owner_headers = register_and_login(client, "funding-owner@example.com")
    _, other_headers = register_and_login(client, "funding-other@example.com")

    first = client.post(
        "/api/v1/funding-sources",
        headers=owner_headers,
        json={
            "type": "CARD",
            "display_name": "Visa personal",
            "provider": "Visa",
            "last_four": "4582",
            "card_number": "4111111111114582",
            "card_expiry": "12/30",
            "card_cvv": "123",
            "currency": "USD",
        },
    )
    assert first.status_code == 201
    assert first.json()["is_default"] is True

    second = client.post(
        "/api/v1/funding-sources",
        headers=owner_headers,
        json={
            "type": "BANK_ACCOUNT",
            "display_name": "Cuenta nomina",
            "provider": "Banco FID",
            "last_four": "7291",
            "account_type": "Ahorro",
            "account_number": "1234567291",
            "currency": "GTQ",
            "is_default": True,
        },
    )
    assert second.status_code == 201
    assert second.json()["is_default"] is True

    owner_list = client.get("/api/v1/funding-sources", headers=owner_headers)
    assert owner_list.status_code == 200
    assert len(owner_list.json()) == 2
    assert sum(1 for item in owner_list.json() if item["is_default"]) == 1

    invalid_currency = client.post(
        "/api/v1/funding-sources",
        headers=owner_headers,
        json={
            "type": "BANK_ACCOUNT",
            "display_name": "Cuenta EUR",
            "provider": "Banco FID",
            "last_four": "1111",
            "account_type": "Monetario",
            "account_number": "1234561111",
            "currency": "EUR",
        },
    )
    assert invalid_currency.status_code == 422

    forbidden = client.patch(
        f"/api/v1/funding-sources/{second.json()['id']}",
        headers=other_headers,
        json={"is_active": False},
    )
    assert forbidden.status_code == 404


def test_transaction_requires_active_compatible_funding_source_and_tracking(client):
    _, sender_headers = register_and_login(client, "tracking-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "tracking-receiver@example.com")

    funding = client.post(
        "/api/v1/funding-sources",
        headers=sender_headers,
        json={
            "type": "CARD",
            "display_name": "Visa USD",
            "provider": "Visa",
            "last_four": "4582",
            "card_number": "4111111111114582",
            "card_expiry": "12/30",
            "card_cvv": "123",
            "currency": "USD",
        },
    ).json()
    beneficiary = client.post(
        "/api/v1/beneficiaries",
        headers=sender_headers,
        json={
            "first_name": "Receiver",
            "last_name": "User",
            "email": receiver["email"],
            "relationship": "Amigo / Amiga",
            "country": "Guatemala",
            "currency": "GTQ",
            "department": "Guatemala",
            "municipality": "Mixco",
            "delivery_method": "BANK_DEPOSIT",
            "account_last_four": "8274",
        },
    ).json()

    created = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
        json={
            "beneficiary_id": beneficiary["id"],
            "origin_country": "Estados Unidos",
            "destination_country": "Guatemala",
            "amount": "400.00",
            "currency": "USD",
            "funding_source_id": funding["id"],
            "payment_method": "BANK_TRANSFER",
            "delivery_method": "BANK_DEPOSIT",
        },
    )
    assert created.status_code == 201
    transaction = created.json()
    assert transaction["funding_source_id"] == funding["id"]
    assert transaction["remittance_uuid"]
    assert transaction["remittance_number"].startswith("FID-")
    assert Decimal(transaction["total_debit_amount"]) == Decimal("409.00")

    sender_tracking = client.get(f"/api/v1/tracking/{transaction['remittance_number']}", headers=sender_headers)
    assert sender_tracking.status_code == 200
    assert sender_tracking.json()["timeline"][0]["new_status"] == "AVAILABLE"

    receiver_tracking = client.get(f"/api/v1/tracking/{transaction['remittance_number']}", headers=receiver_headers)
    assert receiver_tracking.status_code == 200

    client.post(f"/api/v1/transactions/{transaction['id']}/receive", headers=receiver_headers)
    completed_tracking = client.get(f"/api/v1/tracking/{transaction['remittance_number']}", headers=sender_headers)
    assert [item["new_status"] for item in completed_tracking.json()["timeline"]] == ["AVAILABLE", "COMPLETED"]
