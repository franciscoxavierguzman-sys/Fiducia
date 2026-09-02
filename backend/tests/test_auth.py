from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.security.passwords import hash_password


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


def test_legacy_local_domain_user_can_login_and_read_session(client):
    with SessionLocal() as db:
        role = db.scalar(select(Role).where(Role.name == "RISK_ANALYST"))
        assert role is not None
        db.add(
            User(
                first_name="Analista",
                last_name="Legacy",
                email="analista@fiducia.local",
                phone="55550000",
                country="Guatemala",
                password_hash=hash_password("Password123"),
                role_id=role.id,
                document_type="DPI",
                fictitious_document_id="1234567890123",
                birth_date=date(1995, 5, 15),
                occupation="Riesgo",
            )
        )
        db.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "analista@fiducia.local", "password": "Password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "analista@fiducia.local"
    assert me_response.json()["role"]["name"] == "RISK_ANALYST"


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


def test_forgot_password_sends_temporary_password_and_forces_change(client, monkeypatch):
    deliveries = []

    def fake_send_password_reset_email(*, recipient: str, temporary_password: str) -> dict[str, str]:
        deliveries.append({"recipient": recipient, "temporary_password": temporary_password})
        return {"delivery": "simulated_email", "outbox": "test-outbox"}

    monkeypatch.setattr("app.api.v1.endpoints.auth.send_password_reset_email", fake_send_password_reset_email)
    payload = {
        "first_name": "Reset",
        "last_name": "User",
        "email": "reset@example.com",
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
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    reset_response = client.post("/api/v1/auth/password/forgot", json={"email": "reset@example.com"})
    assert reset_response.status_code == 200
    assert reset_response.json()["temporary_password"] == deliveries[0]["temporary_password"]

    old_login = client.post("/api/v1/auth/login", json={"email": "reset@example.com", "password": "Password123"})
    assert old_login.status_code == 401

    temporary_login = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": deliveries[0]["temporary_password"]},
    )
    assert temporary_login.status_code == 200
    assert temporary_login.json()["must_change_password"] is True
    token = temporary_login.json()["access_token"]

    me_response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["must_change_password"] is True

    change_response = client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {token}"},
        json={"new_password": "NewPassword123", "confirm_password": "NewPassword123"},
    )
    assert change_response.status_code == 200
    assert change_response.json()["must_change_password"] is False

    final_login = client.post("/api/v1/auth/login", json={"email": "reset@example.com", "password": "NewPassword123"})
    assert final_login.status_code == 200
    assert final_login.json()["must_change_password"] is False


def test_forgot_password_unknown_email_uses_generic_response(client):
    response = client.post("/api/v1/auth/password/forgot", json={"email": "unknown-reset@example.com"})
    assert response.status_code == 200
    assert response.json()["temporary_password"] is None
    assert "Si el correo esta registrado" in response.json()["message"]


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
