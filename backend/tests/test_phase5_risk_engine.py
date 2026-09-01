from decimal import Decimal

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.risk_assessment import RiskAssessment
from app.risk.aggregator import assign_risk_band, aggregate_risk, recommended_action_for_band
from app.risk.anomaly import anomaly_model_info, predict_anomaly_score
from app.risk.features import amount_bucket
from app.risk.rules import RULES_VERSION, evaluate_rules
from ml.config import TARGET
from scripts.train_anomaly_model import ANOMALY_FEATURES


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "Risk",
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


def create_beneficiary(client, headers):
    response = client.post(
        "/api/v1/beneficiaries",
        headers=headers,
        json={
            "first_name": "Javier",
            "last_name": "Guzman",
            "email": "beneficiary-risk@example.com",
            "relationship": "Amigo / Amiga",
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


def create_remittance(client, headers):
    beneficiary = create_beneficiary(client, headers)
    response = client.post(
        "/api/v1/transactions",
        headers=headers,
        json={
            "beneficiary_id": beneficiary["id"],
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


def high_risk_features():
    return {
        "source_amount": 3000,
        "historical_avg_amount": 400,
        "historical_max_amount": 900,
        "amount_vs_user_average": 7.5,
        "transaction_velocity_24h": 3,
        "transaction_velocity_7d": 6,
        "new_beneficiary_flag": 1,
        "new_corridor_flag": 1,
        "unusual_hour_flag": 1,
        "country_diversity_30d": 3,
        "failed_transaction_ratio": 0.30,
    }


def test_rule_engine_is_versioned_explainable_and_capped():
    result = evaluate_rules(high_risk_features())
    assert result["rules_version"] == RULES_VERSION
    assert result["rule_score"] == 100
    assert result["raw_rule_score"] >= 100
    assert {rule["rule_code"] for rule in result["triggered_rules"]}.issuperset({"R001", "R002", "R004"})
    assert all(rule["reason"] for rule in result["triggered_rules"])


def test_aggregator_handles_unavailable_signal_without_zero_substitution():
    result = aggregate_risk(rule_score=60, ml_probability=0.30, anomaly_score=None)
    assert result.final_risk_score is not None
    assert result.signal_status["anomaly"] == "unavailable"
    assert "anomaly" not in result.weights_used
    assert result.risk_band in {"LOW", "MEDIUM", "HIGH"}


def test_risk_band_boundaries_and_recommended_actions():
    assert assign_risk_band(24.99) == "LOW"
    assert assign_risk_band(25) == "MEDIUM"
    assert assign_risk_band(39.99) == "MEDIUM"
    assert assign_risk_band(40) == "HIGH"
    assert assign_risk_band(72) == "HIGH"
    assert recommended_action_for_band("LOW") == "CONTINUE"
    assert recommended_action_for_band("MEDIUM") == "REVIEW"
    assert recommended_action_for_band("HIGH") == "MANUAL_REVIEW"


def test_anomaly_artifact_is_unsupervised_and_scores_between_zero_and_100():
    info = anomaly_model_info()
    assert info["available"] is True
    assert TARGET in info["excluded_from_training"]
    assert TARGET not in ANOMALY_FEATURES
    features = {
        "source_amount": 980,
        "amount_vs_user_average": 3.77,
        "transaction_velocity_24h": 2,
        "transaction_velocity_7d": 4,
        "transactions_last_30d": 6,
        "beneficiary_age_days": 2,
        "country_diversity_30d": 3,
        "failed_transaction_ratio": 0.5,
        "historical_avg_amount": 260,
        "historical_max_amount": 400,
        "transaction_hour": 2,
        "weekend_flag": 1,
        "new_beneficiary_flag": 1,
        "new_corridor_flag": 1,
        "origin_country": "Estados Unidos",
        "destination_country": "Guatemala",
        "source_currency": "USD",
        "destination_currency": "GTQ",
        "delivery_method": "BANK_DEPOSIT",
        "funding_method": "BANK_TRANSFER",
        "relationship": "Amigo / Amiga",
    }
    result = predict_anomaly_score(features)
    assert 0 <= result["anomaly_score"] <= 100
    assert result["model_version"] == "anomaly-model-v1"


def test_risk_assessment_is_created_with_remittance_and_does_not_block_client_flow(client):
    _, client_headers = register_and_login(client, "phase5-client@example.com")
    transaction = create_remittance(client, client_headers)
    assert transaction["status"] == "AVAILABLE"
    assert transaction["model_version"] == "fraud-model-v1"
    assert Decimal(transaction["final_risk_score"]) >= 0
    with SessionLocal() as db:
        assessments = db.query(RiskAssessment).all()
        assert len(assessments) == 1
        assert assessments[0].risk_engine_version == "risk-engine-v1.1"
        assert assessments[0].ml_threshold == Decimal("0.2500")
        assert assessments[0].risk_band_thresholds_json == {"medium": 25.0, "high": 40.0}


def test_risk_api_permissions_queue_reevaluation_and_human_review(client):
    _, client_headers = register_and_login(client, "risk-client-phase5@example.com")
    _, analyst_headers = register_and_login(client, "risk-analyst-phase5@example.com", role="RISK_ANALYST")
    transaction = create_remittance(client, client_headers)

    forbidden = client.get("/api/v1/risk/assessments", headers=client_headers)
    assert forbidden.status_code == 403

    info = client.get("/api/v1/risk/engine-info", headers=analyst_headers)
    assert info.status_code == 200
    assert info.json()["version"] == "risk-engine-v1.1"
    assert info.json()["ml_threshold"] == 0.25
    assert info.json()["risk_band_thresholds"] == {"medium": 25.0, "high": 40.0}

    queue = client.get("/api/v1/risk/assessments", headers=analyst_headers)
    assert queue.status_code == 200
    assert len(queue.json()) == 1
    assessment_id = queue.json()[0]["id"]

    reevaluation = client.post(f"/api/v1/risk/remittances/{transaction['id']}/evaluate", headers=analyst_headers)
    assert reevaluation.status_code == 200
    assert reevaluation.json()["assessment_sequence"] == 2

    missing_reason = client.post(
        f"/api/v1/risk/assessments/{assessment_id}/review",
        headers=analyst_headers,
        json={"decision": "ESCALATE"},
    )
    assert missing_reason.status_code == 422

    reviewed = client.post(
        f"/api/v1/risk/assessments/{assessment_id}/review",
        headers=analyst_headers,
        json={"decision": "ESCALATE", "reason": "Revision adicional por senales combinadas."},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["review_status"] == "REVIEWED"
    assert reviewed.json()["review_decision"] == "ESCALATE"

    with SessionLocal() as db:
        actions = {event.action for event in db.query(AuditLog).all()}
        assert "RISK_ASSESSMENT_CREATED" in actions
        assert "RISK_ASSESSMENT_REEVALUATED" in actions
        assert "RISK_REVIEW_ESCALATED" in actions


def test_amount_bucket_boundaries():
    assert amount_bucket(Decimal("99.99")) == "0-99"
    assert amount_bucket(Decimal("100.00")) == "100-499"
    assert amount_bucket(Decimal("500.00")) == "500-999"


def test_explicit_reevaluation_preserves_historical_assessment_snapshot(client):
    _, client_headers = register_and_login(client, "snapshot-client-phase5@example.com")
    _, analyst_headers = register_and_login(client, "snapshot-analyst-phase5@example.com", role="RISK_ANALYST")
    transaction = create_remittance(client, client_headers)

    with SessionLocal() as db:
        original = db.query(RiskAssessment).one()
        original.risk_engine_version = "risk-engine-v1"
        original.risk_band_thresholds_json = {"medium": 25.0, "high": 50.0}
        db.commit()
        original_id = original.id

    reevaluation = client.post(f"/api/v1/risk/remittances/{transaction['id']}/evaluate", headers=analyst_headers)
    assert reevaluation.status_code == 200
    assert reevaluation.json()["risk_engine_version"] == "risk-engine-v1.1"
    assert reevaluation.json()["risk_band_thresholds_json"] == {"medium": 25.0, "high": 40.0}

    with SessionLocal() as db:
        original = db.get(RiskAssessment, original_id)
        assert original.risk_engine_version == "risk-engine-v1"
        assert original.risk_band_thresholds_json == {"medium": 25.0, "high": 50.0}
        assert db.query(RiskAssessment).count() == 2
