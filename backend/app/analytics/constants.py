from decimal import Decimal


COUNTRY_CURRENCIES = {
    "Estados Unidos": "USD",
    "Guatemala": "GTQ",
    "Canada": "CAD",
    "Mexico": "MXN",
    "Espana": "EUR",
}

EXCHANGE_RATES_TO_USD = {
    "USD": Decimal("1.000000"),
    "GTQ": Decimal("0.128205"),
    "CAD": Decimal("0.740000"),
    "MXN": Decimal("0.055000"),
    "EUR": Decimal("1.090000"),
}

STATUSES = {
    "AVAILABLE",
    "COMPLETED",
    "PROCESSING",
    "REVIEW_REQUIRED",
    "REJECTED",
}

PAYMENT_METHODS = {"BANK_TRANSFER", "DEBIT_CARD", "DIGITAL_WALLET"}
DELIVERY_METHODS = {"BANK_DEPOSIT", "TRANSFER", "WALLET", "CASH_PICKUP"}

MONEY_FIELDS = {
    "source_amount",
    "commission_rate",
    "commission_amount",
    "total_debit_amount",
    "exchange_rate",
    "destination_amount",
    "historical_amount",
    "avg_transaction_amount",
    "max_transaction_amount",
    "amount_vs_user_average",
    "historical_avg_amount",
    "historical_max_amount",
    "rule_score",
    "ml_probability",
    "anomaly_score",
    "final_risk_score",
}

REQUIRED_FIELDS = [
    "user_id",
    "country",
    "account_age_days",
    "transaction_count",
    "historical_amount",
    "registration_date",
    "remittance_id",
    "remittance_number",
    "origin_country",
    "destination_country",
    "source_currency",
    "destination_currency",
    "source_amount",
    "commission_rate",
    "commission_amount",
    "total_debit_amount",
    "exchange_rate",
    "destination_amount",
    "delivery_method",
    "funding_method",
    "status",
    "created_at",
    "beneficiary_id",
    "relationship",
    "linked_user",
    "transactions_last_24h",
    "transactions_last_7d",
    "transactions_last_30d",
    "avg_transaction_amount",
    "max_transaction_amount",
    "new_beneficiary",
    "beneficiary_age_days",
    "countries_used_last_30d",
    "failed_transactions",
    "transaction_hour",
    "weekend_transaction",
    "amount_vs_user_average",
    "transaction_velocity_24h",
    "transaction_velocity_7d",
    "new_beneficiary_flag",
    "unusual_hour_flag",
    "weekend_flag",
    "new_corridor_flag",
    "country_diversity_30d",
    "failed_transaction_ratio",
    "historical_avg_amount",
    "historical_max_amount",
    "rule_score",
    "ml_probability",
    "anomaly_score",
    "final_risk_score",
    "fraud_label",
]

