def test_register_login_and_read_me(client):
    user_payload = {
        "first_name": "Ana",
        "last_name": "Lopez",
        "email": "ana@example.com",
        "phone": "55551234",
        "country": "Guatemala",
        "password": "Password123",
        "confirm_password": "Password123",
        "terms_accepted": True,
        "human_check_accepted": True,
        "document_type": "DPI",
        "fictitious_document_id": "1234567890123",
        "birth_date": "1995-05-15",
        "occupation": "Estudiante",
    }

    register_response = client.post("/api/v1/auth/register", json=user_payload)
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["email"] == "ana@example.com"
    assert body["document_type"] == "DPI"
    assert body["fictitious_document_id"] == "1234567890123"
    assert body["birth_date"] == "1995-05-15"
    assert body["role"]["name"] == "CLIENT"
    assert "password" not in body
    assert "password_hash" not in body

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "ana@example.com", "password": "Password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ana@example.com"


def test_protected_endpoint_rejects_missing_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token(client):
    response = client.get("/api/v1/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


def test_login_rejects_wrong_password(client):
    payload = {
        "first_name": "Maria",
        "last_name": "Perez",
        "email": "maria@example.com",
        "phone": "55551111",
        "country": "Guatemala",
        "password": "Password123",
        "confirm_password": "Password123",
        "terms_accepted": True,
        "human_check_accepted": True,
        "document_type": "DPI",
        "fictitious_document_id": "1234567890123",
        "birth_date": "1995-05-15",
    }

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "maria@example.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_login_rejects_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "Password123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_duplicate_email_is_rejected(client):
    payload = {
        "first_name": "Luis",
        "last_name": "Garcia",
        "email": "luis@example.com",
        "phone": "55550000",
        "country": "Estados Unidos",
        "password": "Password123",
        "confirm_password": "Password123",
        "terms_accepted": True,
        "human_check_accepted": True,
        "document_type": "PASSPORT",
        "fictitious_document_id": "PA123456",
        "birth_date": "1990-01-20",
    }

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/api/v1/auth/register", json=payload)
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_rejects_invalid_password_country_and_terms(client):
    base_payload = {
        "first_name": "Laura",
        "last_name": "Diaz",
        "email": "laura@example.com",
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

    weak_password = dict(base_payload, email="weak@example.com", password="password", confirm_password="password")
    assert client.post("/api/v1/auth/register", json=weak_password).status_code == 422

    mismatch = dict(base_payload, email="mismatch@example.com", confirm_password="Other12345")
    assert client.post("/api/v1/auth/register", json=mismatch).status_code == 422

    missing_terms = dict(base_payload, email="terms@example.com", terms_accepted=False)
    assert client.post("/api/v1/auth/register", json=missing_terms).status_code == 422

    missing_human_check = dict(base_payload, email="human@example.com", human_check_accepted=False)
    assert client.post("/api/v1/auth/register", json=missing_human_check).status_code == 422

    invalid_dpi = dict(base_payload, email="dpi@example.com", fictitious_document_id="12345")
    assert client.post("/api/v1/auth/register", json=invalid_dpi).status_code == 422

    missing_birth_date = dict(base_payload, email="birth@example.com", birth_date=None)
    assert client.post("/api/v1/auth/register", json=missing_birth_date).status_code == 422

    future_birth_date = dict(base_payload, email="future@example.com", birth_date="2999-01-01")
    assert client.post("/api/v1/auth/register", json=future_birth_date).status_code == 422

    invalid_country = dict(base_payload, email="country@example.com", country="Francia")
    response = client.post("/api/v1/auth/register", json=invalid_country)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_COUNTRY"
