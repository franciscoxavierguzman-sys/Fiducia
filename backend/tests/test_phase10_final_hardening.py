from app.db.session import SessionLocal
from app.models.audit_log import AuditLog


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "Final",
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


def create_beneficiary(client, headers, email: str):
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json={
            "first_name": "Demo",
            "last_name": "Receiver",
            "email": email,
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
    assert response.status_code == 201
    return response.json()


def create_remittance(client, headers, beneficiary_id: int):
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "beneficiary_id": beneficiary_id,
            "origin_country": "Estados Unidos",
            "destination_country": "Guatemala",
            "amount": "250.00",
            "currency": "USD",
            "payment_method": "BANK_TRANSFER",
            "delivery_method": "BANK_DEPOSIT",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_ready_request_id_and_security_headers(client):
    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"
    assert response.headers["X-Request-ID"] == "test-request-id"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"


def test_cors_allows_localhost_and_127_development_origins(client):
    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        response = client.options(
            "/api/v1/blockchain/info",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == origin

        unauthorized_response = client.get("/api/v1/blockchain/info", headers={"Origin": origin})
        assert unauthorized_response.status_code == 401
        assert unauthorized_response.headers["Access-Control-Allow-Origin"] == origin


def test_cors_does_not_authorize_unknown_origin(client):
    response = client.options(
        "/api/v1/blockchain/info",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 400
    assert "Access-Control-Allow-Origin" not in response.headers

    unauthorized_response = client.get("/api/v1/blockchain/info", headers={"Origin": "http://evil.example"})
    assert unauthorized_response.status_code == 401
    assert "Access-Control-Allow-Origin" not in unauthorized_response.headers


def test_system_info_and_metrics_are_admin_only(client):
    _, client_headers = register_and_login(client, "phase10-client@example.com")
    _, admin_headers = register_and_login(client, "phase10-admin@example.com", role="ADMIN")

    denied = client.get("/api/v1/system/info", headers=client_headers)
    info = client.get("/api/v1/system/info", headers=admin_headers)
    metrics = client.get("/api/v1/system/metrics", headers=admin_headers)

    assert denied.status_code == 403
    assert info.status_code == 200
    assert info.json()["app_version"] == "1.0.0"
    assert info.json()["ml_threshold"] == 0.25
    assert "assistant_provider_type" in info.json()
    assert metrics.status_code == 200
    assert metrics.json()["requests"]["requests_total"] >= 1


def test_login_rate_limit_returns_friendly_error(client):
    register_and_login(client, "phase10-rate@example.com")

    last_response = None
    for _ in range(13):
        last_response = client.post("/api/v1/auth/login", json={"email": "phase10-rate@example.com", "password": "bad-password"})

    assert last_response is not None
    assert last_response.status_code == 429
    assert last_response.json()["detail"]["code"] == "RATE_LIMITED"


def test_cross_role_security_regression(client):
    _, owner_headers = register_and_login(client, "phase10-owner@example.com")
    _, other_headers = register_and_login(client, "phase10-other@example.com")
    _, analyst_headers = register_and_login(client, "phase10-risk@example.com", role="RISK_ANALYST")
    beneficiary = create_beneficiary(client, owner_headers, "phase10-beneficiary@example.com")
    remittance = create_remittance(client, owner_headers, beneficiary["id"])

    assert client.get("/api/v1/bi/overview", headers=other_headers).status_code == 403
    assert client.get("/api/v1/risk/dashboard", headers=other_headers).status_code == 403
    assert client.get("/api/v1/blockchain/blocks", headers=other_headers).status_code == 403
    assert client.get(f"/api/v1/transactions/{remittance['id']}", headers=other_headers).status_code == 404
    assert client.get(f"/api/v1/blockchain/verify/{remittance['id']}", headers=other_headers).status_code == 404
    assert client.get("/api/v1/risk/dashboard", headers=analyst_headers).status_code == 200


def test_audit_contains_final_flow_events(client):
    _, headers = register_and_login(client, "phase10-audit@example.com")
    beneficiary = create_beneficiary(client, headers, "phase10-audit-beneficiary@example.com")
    create_remittance(client, headers, beneficiary["id"])
    client.post("/api/v1/assistant/chat", headers=headers, json={"message": "Cual es el estado de mi ultima remesa?"})

    with SessionLocal() as db:
        actions = {item.action for item in db.query(AuditLog).all()}

    assert "LOGIN" in actions
    assert "BENEFICIARY_CREATED" in actions
    assert "REMITTANCE_CREATED" in actions
    assert "RISK_ASSESSMENT_CREATED" in actions
    assert "ASSISTANT_RESPONSE_GENERATED" in actions
