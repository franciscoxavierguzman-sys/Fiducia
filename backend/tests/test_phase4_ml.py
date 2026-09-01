import csv
import sys
from decimal import Decimal
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services import ml_risk
from ml.config import EXCLUDED_FEATURES, FEATURES
from ml.training.train import audit_feature_leakage, load_dataset, train_fraud_model


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
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123"},
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def sample_features():
    with (PROJECT_ROOT / "data" / "processed" / "remittances_analytics.csv").open("r", encoding="utf-8", newline="") as file:
        row = next(csv.DictReader(file))
    return {feature: row[feature] for feature in FEATURES}


def test_feature_list_excludes_known_leakage_columns():
    assert "fraud_label" not in FEATURES
    assert "ml_probability" not in FEATURES
    assert "final_risk_score" not in FEATURES
    assert not set(FEATURES).intersection(EXCLUDED_FEATURES)


def test_training_produces_reproducible_metadata(tmp_path: Path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    report_dir = tmp_path / "reports"
    dataset = PROJECT_ROOT / "data" / "processed" / "remittances_analytics.csv"

    first = train_fraud_model(dataset_path=dataset, artifact_dir=first_dir, report_dir=report_dir / "a", seed=42)
    second = train_fraud_model(dataset_path=dataset, artifact_dir=second_dir, report_dir=report_dir / "b", seed=42)

    assert first["metadata"]["dataset_hash"] == second["metadata"]["dataset_hash"]
    assert first["metadata"]["selected_model"] == second["metadata"]["selected_model"]
    assert first["metadata"]["model_version"] == "fraud-model-v1"
    assert first["metadata"]["threshold"] == second["metadata"]["threshold"]
    assert first_dir.joinpath("fraud_model.joblib").exists()
    assert first_dir.joinpath("model_metadata.json").exists()
    assert first_dir.joinpath("model_metrics.json").exists()


def test_dataset_load_and_leakage_audit_are_valid():
    data = load_dataset(PROJECT_ROOT / "data" / "processed" / "remittances_analytics.csv")
    report = audit_feature_leakage(data)
    assert len(data) == 10000
    assert report["valid"] is True
    assert report["included_overlap"] == []


def test_ml_risk_inference_returns_probability_range():
    ml_risk._load_model_artifact.cache_clear()
    result = ml_risk.predict_fraud_probability(sample_features())
    assert 0 <= result.ml_probability <= 1
    assert result.model_version == "fraud-model-v1"
    assert result.threshold == 0.25
    assert result.classification in {"LOW", "MEDIUM", "HIGH"}


def test_ml_risk_rejects_missing_features():
    with pytest.raises(Exception):
        ml_risk.predict_fraud_probability({"source_amount": 100})


def test_risk_api_authorization_and_prediction(client):
    _, client_headers = register_and_login(client, "risk-client@example.com")
    _, analyst_headers = register_and_login(client, "risk-analyst@example.com", role="RISK_ANALYST")

    forbidden = client.get("/api/v1/risk/ml/model-info", headers=client_headers)
    assert forbidden.status_code == 403

    info = client.get("/api/v1/risk/ml/model-info", headers=analyst_headers)
    assert info.status_code == 200
    assert info.json()["available"] is True
    assert info.json()["threshold"] == 0.25

    metrics = client.get("/api/v1/risk/ml/metrics", headers=analyst_headers)
    assert metrics.status_code == 200
    assert metrics.json()["selected_model"]

    prediction = client.post("/api/v1/risk/ml/predict", headers=analyst_headers, json={"features": sample_features()})
    assert prediction.status_code == 200
    assert 0 <= Decimal(str(prediction.json()["ml_probability"])) <= 1
    assert prediction.json()["threshold"] == 0.25


def test_missing_model_is_reported_without_crashing(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(ml_risk, "ARTIFACT_PATH", tmp_path / "missing.joblib")
    monkeypatch.setattr(ml_risk, "METADATA_PATH", tmp_path / "missing_metadata.json")
    ml_risk._load_model_artifact.cache_clear()

    info = ml_risk.get_model_info()
    assert info.available is False
    with pytest.raises(Exception):
        ml_risk.predict_fraud_probability(sample_features())
