from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def build_operational_features(db: Session, transaction: Transaction) -> dict[str, Any]:
    created_at = _as_utc(transaction.created_at)
    prior_transactions = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.sender_id == transaction.sender_id, Transaction.id != transaction.id, Transaction.created_at <= transaction.created_at)
            .order_by(Transaction.created_at.asc())
        )
    )
    beneficiary_history = [item for item in prior_transactions if item.beneficiary_id == transaction.beneficiary_id]
    corridor_history = [
        item
        for item in prior_transactions
        if item.origin_country == transaction.origin_country and item.destination_country == transaction.destination_country
    ]
    last_24h = [item for item in prior_transactions if _as_utc(item.created_at) >= created_at - timedelta(hours=24)]
    last_7d = [item for item in prior_transactions if _as_utc(item.created_at) >= created_at - timedelta(days=7)]
    last_30d = [item for item in prior_transactions if _as_utc(item.created_at) >= created_at - timedelta(days=30)]
    amounts = [Decimal(item.source_amount) for item in prior_transactions]
    avg_amount = sum(amounts, Decimal("0")) / Decimal(len(amounts)) if amounts else Decimal("0")
    max_amount = max(amounts) if amounts else Decimal("0")
    source_amount = Decimal(transaction.source_amount)
    failed_statuses = {"REJECTED", "FAILED", "CANCELLED", "REVIEW_REQUIRED"}
    failed_transactions = len([item for item in prior_transactions if item.status in failed_statuses])
    failed_ratio = Decimal(failed_transactions) / Decimal(len(prior_transactions)) if prior_transactions else Decimal("0")
    beneficiary_created_at = _as_utc(transaction.beneficiary.created_at) if transaction.beneficiary else created_at
    beneficiary_age_days = max(0, (created_at - beneficiary_created_at).days)
    amount_vs_avg = source_amount / avg_amount if avg_amount > 0 else Decimal("1")
    countries_last_30d = len({item.destination_country for item in last_30d})

    return {
        "account_age_days": max(0, (created_at - _as_utc(transaction.sender.created_at)).days) if transaction.sender else 0,
        "transaction_count": len(prior_transactions),
        "source_amount": float(source_amount),
        "commission_rate": float(transaction.commission_rate),
        "commission_amount": float(transaction.commission_amount),
        "total_debit_amount": float(transaction.debit_amount or transaction.total_amount),
        "exchange_rate": float(transaction.exchange_rate),
        "destination_amount": float(transaction.destination_amount),
        "linked_user": 1 if transaction.beneficiary_user_id else 0,
        "transactions_last_24h": len(last_24h),
        "transactions_last_7d": len(last_7d),
        "transactions_last_30d": len(last_30d),
        "avg_transaction_amount": float(avg_amount),
        "max_transaction_amount": float(max_amount),
        "new_beneficiary_flag": 1 if not beneficiary_history or beneficiary_age_days <= 7 else 0,
        "beneficiary_age_days": beneficiary_age_days,
        "countries_used_last_30d": countries_last_30d,
        "failed_transactions": failed_transactions,
        "transaction_hour": created_at.hour,
        "weekend_flag": 1 if created_at.weekday() >= 5 else 0,
        "amount_vs_user_average": float(amount_vs_avg),
        "transaction_velocity_24h": len(last_24h),
        "transaction_velocity_7d": len(last_7d),
        "unusual_hour_flag": 1 if created_at.hour <= 5 else 0,
        "new_corridor_flag": 1 if not corridor_history else 0,
        "country_diversity_30d": countries_last_30d,
        "failed_transaction_ratio": float(failed_ratio),
        "historical_avg_amount": float(avg_amount),
        "historical_max_amount": float(max_amount),
        "origin_country": transaction.origin_country,
        "destination_country": transaction.destination_country,
        "source_currency": transaction.source_currency,
        "destination_currency": transaction.destination_currency,
        "delivery_method": transaction.delivery_method,
        "funding_method": transaction.payment_method,
        "relationship": transaction.beneficiary.relationship if transaction.beneficiary else "Otro",
        "amount_bucket": amount_bucket(source_amount),
    }


def amount_bucket(value: Decimal) -> str:
    if value < Decimal("100"):
        return "0-99"
    if value < Decimal("500"):
        return "100-499"
    if value < Decimal("1000"):
        return "500-999"
    if value < Decimal("2500"):
        return "1000-2499"
    return "2500+"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
