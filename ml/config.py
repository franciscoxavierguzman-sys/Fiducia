from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "remittances_analytics.csv"
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"
REPORT_DIR = PROJECT_ROOT / "reports" / "ml"

MODEL_NAME = "FIDUCIA Fraud Probability Model"
MODEL_VERSION = "fraud-model-v1"
TARGET = "fraud_label"

NUMERIC_FEATURES = [
    "account_age_days",
    "transaction_count",
    "source_amount",
    "commission_rate",
    "commission_amount",
    "total_debit_amount",
    "exchange_rate",
    "destination_amount",
    "linked_user",
    "transactions_last_24h",
    "transactions_last_7d",
    "transactions_last_30d",
    "avg_transaction_amount",
    "max_transaction_amount",
    "new_beneficiary_flag",
    "beneficiary_age_days",
    "countries_used_last_30d",
    "failed_transactions",
    "transaction_hour",
    "weekend_flag",
    "amount_vs_user_average",
    "transaction_velocity_24h",
    "transaction_velocity_7d",
    "unusual_hour_flag",
    "new_corridor_flag",
    "country_diversity_30d",
    "failed_transaction_ratio",
    "historical_avg_amount",
    "historical_max_amount",
]

CATEGORICAL_FEATURES = [
    "origin_country",
    "destination_country",
    "source_currency",
    "destination_currency",
    "delivery_method",
    "funding_method",
    "relationship",
    "amount_bucket",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

EXCLUDED_FEATURES = [
    "fraud_label",
    "rule_score",
    "ml_probability",
    "anomaly_score",
    "final_risk_score",
    "risk_band_experimental",
    "status",
    "completed_at",
    "remittance_id",
    "remittance_number",
    "user_id",
    "beneficiary_id",
    "registration_date",
    "created_at",
    "historical_amount",
    "new_beneficiary",
    "weekend_transaction",
    "is_cross_border",
]

