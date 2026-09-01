import pandas as pd

from app.forecasting.audit import temporal_audit
from app.forecasting.evaluation import chronological_split, evaluate_models
from app.forecasting.preprocessing import FORECASTING_DATASET_PATH, PROCESSED_DATASET_PATH, build_weekly_series, load_remittance_dataset
from app.models.forecast import ForecastRun, ForecastValue
from app.services.forecasting import generate_forecast, get_forecast_model_info


def register_and_login(client, email: str, role: str = "CLIENT"):
    payload = {
        "first_name": "Forecast",
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


def test_temporal_audit_supports_conditional_weekly_forecasting():
    report = temporal_audit(PROCESSED_DATASET_PATH)
    assert report["go_decision"] == "CONDITIONAL"
    assert report["weeks_covered"] >= 52
    assert report["recommended_granularity"] == "weekly"
    assert report["continuity"] == "weekly_continuous"


def test_weekly_series_is_ordered_complete_and_uses_usd_equivalent():
    data = load_remittance_dataset(PROCESSED_DATASET_PATH)
    weekly = build_weekly_series(data)
    assert len(weekly) == 78
    assert weekly["period"].is_monotonic_increasing
    assert weekly["transaction_count"].min() > 0
    assert weekly["transaction_amount_usd"].sum() > 0


def test_chronological_split_avoids_future_leakage():
    series = pd.read_csv(FORECASTING_DATASET_PATH, parse_dates=["period"])
    train, validation, test = chronological_split(series)
    assert train["period"].max() < validation["period"].min()
    assert validation["period"].max() < test["period"].min()


def test_forecast_model_training_is_reproducible_and_selects_by_validation():
    series = pd.read_csv(FORECASTING_DATASET_PATH, parse_dates=["period"])
    results, selected = evaluate_models(series, "transaction_count")
    selected_result = next(item for item in results if item.name == selected)
    best_validation_wape = min(item.validation["wape"] for item in results)
    assert selected_result.validation["wape"] == best_validation_wape
    assert selected == "Moving Average 8"


def test_forecast_service_generates_allowed_horizon_and_intervals():
    response = generate_forecast("transaction_count", 4)
    assert response["model_version"] == "remittance-forecast-v1"
    assert response["horizon"] == 4
    assert len(response["forecast"]) == 4
    assert response["forecast"][0]["lower_80"] <= response["forecast"][0]["predicted"] <= response["forecast"][0]["upper_80"]


def test_forecasting_api_permissions_validation_and_persistence(client):
    _, client_headers = register_and_login(client, "forecast-client@example.com")
    _, analyst_headers = register_and_login(client, "forecast-analyst@example.com", role="RISK_ANALYST")

    forbidden = client.get("/api/v1/forecasting/model-info", headers=client_headers)
    assert forbidden.status_code == 403

    info = client.get("/api/v1/forecasting/model-info", headers=analyst_headers)
    assert info.status_code == 200
    assert info.json()["available"] is True
    assert info.json()["version"] == "remittance-forecast-v1"

    invalid_horizon = client.get("/api/v1/forecasting/volume?horizon=99", headers=analyst_headers)
    assert invalid_horizon.status_code == 422
    assert invalid_horizon.json()["detail"]["code"] == "INVALID_HORIZON"

    invalid_target = client.get("/api/v1/forecasting/volume?granularity=daily", headers=analyst_headers)
    assert invalid_target.status_code == 422
    assert invalid_target.json()["detail"]["code"] == "INVALID_GRANULARITY"

    forecast = client.get("/api/v1/forecasting/volume?horizon=4", headers=analyst_headers)
    assert forecast.status_code == 200
    assert len(forecast.json()["forecast"]) == 4

def test_forecast_model_info_reports_targets():
    info = get_forecast_model_info()
    assert info["available"] is True
    assert "transaction_count" in info["targets"]
    assert "transaction_amount_usd" in info["targets"]


def test_forecast_persistence_directly(client):
    _, analyst_headers = register_and_login(client, "forecast-persist@example.com", role="ADMIN")
    response = client.get("/api/v1/forecasting/amount?horizon=4", headers=analyst_headers)
    assert response.status_code == 200
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        assert db.query(ForecastRun).count() == 1
        assert db.query(ForecastValue).count() == 4
