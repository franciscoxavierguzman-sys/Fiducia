def register_user(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": role.title(),
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
        "occupation": "Soporte" if role == "SUPPORT" else "Cliente",
        "role": role,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return response.json()


def login(client, email: str, password: str = "Password123") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_support_can_list_users_reset_password_and_unlock(client, monkeypatch):
    deliveries = []

    def fake_send_password_reset_email(*, recipient: str, temporary_password: str) -> dict[str, str]:
        deliveries.append({"recipient": recipient, "temporary_password": temporary_password})
        return {"delivery": "simulated_email", "outbox": "test-outbox"}

    monkeypatch.setattr("app.api.v1.endpoints.users.send_password_reset_email", fake_send_password_reset_email)

    support = register_user(client, "support@example.com", "SUPPORT")
    client_user = register_user(client, "client@example.com", "CLIENT")
    support_token = login(client, "support@example.com")

    list_response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {support_token}"})
    assert list_response.status_code == 200
    emails = {user["email"] for user in list_response.json()}
    assert {"support@example.com", "client@example.com"}.issubset(emails)

    reset_response = client.post(
        f"/api/v1/users/{client_user['id']}/password-reset",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert reset_response.status_code == 200
    temporary_password = reset_response.json()["temporary_password"]
    assert deliveries == [{"recipient": "client@example.com", "temporary_password": temporary_password}]
    assert reset_response.json()["user"]["must_change_password"] is True

    old_login = client.post("/api/v1/auth/login", json={"email": "client@example.com", "password": "Password123"})
    assert old_login.status_code == 401

    temporary_login = client.post(
        "/api/v1/auth/login",
        json={"email": "client@example.com", "password": temporary_password},
    )
    assert temporary_login.status_code == 200
    assert temporary_login.json()["must_change_password"] is True

    lock_response = client.post(f"/api/v1/users/{client_user['id']}/lock", headers={"Authorization": f"Bearer {support_token}"})
    assert lock_response.status_code == 200
    assert lock_response.json()["is_active"] is False

    locked_login = client.post("/api/v1/auth/login", json={"email": "client@example.com", "password": temporary_password})
    assert locked_login.status_code == 403
    assert locked_login.json()["detail"]["code"] == "USER_LOCKED"

    unlock_response = client.post(
        f"/api/v1/users/{client_user['id']}/unlock",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert unlock_response.status_code == 200
    assert unlock_response.json()["is_active"] is True

    assert support["role"]["name"] == "SUPPORT"


def test_client_cannot_use_support_user_administration(client):
    register_user(client, "support@example.com", "SUPPORT")
    register_user(client, "client@example.com", "CLIENT")
    client_token = login(client, "client@example.com")

    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {client_token}"})

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "SUPPORT_ACCESS_REQUIRED"


def test_support_cannot_lock_self(client):
    support = register_user(client, "support@example.com", "SUPPORT")
    support_token = login(client, "support@example.com")

    response = client.post(f"/api/v1/users/{support['id']}/lock", headers={"Authorization": f"Bearer {support_token}"})

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "CANNOT_LOCK_SELF"
