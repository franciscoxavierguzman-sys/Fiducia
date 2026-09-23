def register_and_login(client, email: str):
    payload = {
        "first_name": "Market",
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
    token = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"}).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def create_received_remittance(client, sender_headers, receiver_headers, receiver_email: str):
    beneficiary = client.post(
        "/api/v1/beneficiaries",
        headers=sender_headers,
        json={
            "first_name": "Compra",
            "last_name": "Marketplace",
            "email": receiver_email,
            "relationship": "Madre",
            "country": "Guatemala",
            "currency": "GTQ",
            "department": "Guatemala",
            "municipality": "Guatemala",
            "delivery_method": "BANK_DEPOSIT",
            "bank_name": "Banco Simulado",
            "account_type": "Ahorro",
            "account_last_four": "1234",
        },
    )
    assert beneficiary.status_code == 201
    transaction = client.post(
        "/api/v1/transactions",
        headers=sender_headers,
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
    assert transaction.status_code == 201
    receive = client.post(f"/api/v1/transactions/{transaction.json()['id']}/receive", headers=receiver_headers)
    assert receive.status_code == 200
    return receive.json()


def test_marketplace_purchase_uses_completed_received_remittance_balance(client):
    _, sender_headers = register_and_login(client, "market-sender@example.com")
    receiver, receiver_headers = register_and_login(client, "market-receiver@example.com")
    remittance = create_received_remittance(client, sender_headers, receiver_headers, receiver["email"])

    products_response = client.get("/api/v1/marketplace/products", headers=receiver_headers)
    assert products_response.status_code == 200
    product = products_response.json()[0]

    balances_response = client.get("/api/v1/marketplace/balances", headers=receiver_headers)
    assert balances_response.status_code == 200
    balance = balances_response.json()[0]
    assert balance["transaction_id"] == remittance["id"]
    assert float(balance["available_amount"]) > float(product["price_amount"])

    order_response = client.post(
        "/api/v1/marketplace/orders",
        headers=receiver_headers,
        json={"remittance_transaction_id": remittance["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
    )
    assert order_response.status_code == 201
    order = order_response.json()
    assert order["order_number"].startswith("MKT-")
    assert order["total_amount"] == product["price_amount"]
    assert order["items"][0]["product"]["id"] == product["id"]

    updated_balance = client.get("/api/v1/marketplace/balances", headers=receiver_headers).json()[0]
    assert updated_balance["spent_amount"] == product["price_amount"]

    orders_response = client.get("/api/v1/marketplace/orders", headers=receiver_headers)
    assert orders_response.status_code == 200
    assert orders_response.json()[0]["id"] == order["id"]


def test_marketplace_rejects_sender_and_insufficient_balance(client):
    _, sender_headers = register_and_login(client, "market-sender-2@example.com")
    receiver, receiver_headers = register_and_login(client, "market-receiver-2@example.com")
    remittance = create_received_remittance(client, sender_headers, receiver_headers, receiver["email"])
    product = client.get("/api/v1/marketplace/products", headers=receiver_headers).json()[0]

    sender_order = client.post(
        "/api/v1/marketplace/orders",
        headers=sender_headers,
        json={"remittance_transaction_id": remittance["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
    )
    assert sender_order.status_code == 404
    assert sender_order.json()["detail"]["code"] == "REMITTANCE_NOT_FOUND"

    expensive_order = client.post(
        "/api/v1/marketplace/orders",
        headers=receiver_headers,
        json={"remittance_transaction_id": remittance["id"], "items": [{"product_id": product["id"], "quantity": 20}]},
    )
    assert expensive_order.status_code == 400
    assert expensive_order.json()["detail"]["code"] == "INSUFFICIENT_REMITTANCE_BALANCE"
