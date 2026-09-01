from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.constants import EXCHANGE_RATES_TO_USD
from app.bi.definitions import BI_ELIGIBLE_STATUSES, COMPLETED_STATUS, RISK_BAND_LABELS, STATUS_LABELS, round_money, round_ratio, safe_divide
from app.bi.filters import BIFilters, apply_transaction_filters
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction


def money_to_usd(amount: Decimal, currency: str) -> Decimal:
    return Decimal(amount) * Decimal(EXCHANGE_RATES_TO_USD.get(currency, Decimal("0")))


def filtered_transactions(db: Session, filters: BIFilters) -> list[Transaction]:
    statement = apply_transaction_filters(select(Transaction), filters).order_by(Transaction.created_at)
    return list(db.scalars(statement).all())


def calculate_overview(db: Session, filters: BIFilters) -> dict:
    transactions = filtered_transactions(db, filters)
    total = len(transactions)
    total_amount = sum((money_to_usd(tx.source_amount, tx.source_currency) for tx in transactions), Decimal("0"))
    commission_revenue = sum((money_to_usd(tx.commission_amount, tx.source_currency) for tx in transactions), Decimal("0"))
    active_clients = len({tx.sender_id for tx in transactions})
    active_corridors = len({(tx.origin_country, tx.destination_country) for tx in transactions})
    eligible = [tx for tx in transactions if tx.status in BI_ELIGIBLE_STATUSES or tx.status == COMPLETED_STATUS]
    completed = [tx for tx in eligible if tx.status == COMPLETED_STATUS]
    return {
        "total_remittances": total,
        "total_amount_usd_equivalent": round_money(total_amount),
        "average_ticket_usd_equivalent": round_money(safe_divide(total_amount, total)),
        "total_commission_revenue_usd_equivalent": round_money(commission_revenue),
        "average_commission_usd_equivalent": round_money(safe_divide(commission_revenue, total)),
        "active_clients": active_clients,
        "active_corridors": active_corridors,
        "completion_rate": round_ratio(safe_divide(len(completed), len(eligible))),
    }


def calculate_trends(db: Session, filters: BIFilters, granularity: str = "week") -> list[dict]:
    transactions = filtered_transactions(db, filters)
    buckets: dict[str, dict] = defaultdict(lambda: {"period": "", "remittances": 0, "amount_usd_equivalent": Decimal("0"), "commission_revenue_usd_equivalent": Decimal("0")})
    for tx in transactions:
        period = _period_key(tx.created_at, granularity)
        buckets[period]["period"] = period
        buckets[period]["remittances"] += 1
        buckets[period]["amount_usd_equivalent"] += money_to_usd(tx.source_amount, tx.source_currency)
        buckets[period]["commission_revenue_usd_equivalent"] += money_to_usd(tx.commission_amount, tx.source_currency)
    return [
        {
            "period": row["period"],
            "remittances": row["remittances"],
            "amount_usd_equivalent": round_money(row["amount_usd_equivalent"]),
            "commission_revenue_usd_equivalent": round_money(row["commission_revenue_usd_equivalent"]),
        }
        for _, row in sorted(buckets.items())
    ]


def calculate_corridors(db: Session, filters: BIFilters) -> list[dict]:
    transactions = filtered_transactions(db, filters)
    grouped: dict[tuple[str, str], list[Transaction]] = defaultdict(list)
    risk_counts = _risk_counts_by_remittance(db)
    for tx in transactions:
        grouped[(tx.origin_country, tx.destination_country)].append(tx)
    rows = []
    for (origin, destination), items in grouped.items():
        total_amount = sum((money_to_usd(tx.source_amount, tx.source_currency) for tx in items), Decimal("0"))
        commission = sum((money_to_usd(tx.commission_amount, tx.source_currency) for tx in items), Decimal("0"))
        completed = sum(1 for tx in items if tx.status == COMPLETED_STATUS)
        risk_counter = Counter()
        for tx in items:
            risk_counter.update(risk_counts.get(tx.id, []))
        total_risk = sum(risk_counter.values())
        rows.append(
            {
                "origin_country": origin,
                "destination_country": destination,
                "corridor": f"{origin} -> {destination}",
                "remittance_count": len(items),
                "total_amount_usd_equivalent": round_money(total_amount),
                "average_ticket_usd_equivalent": round_money(safe_divide(total_amount, len(items))),
                "commission_revenue_usd_equivalent": round_money(commission),
                "completion_rate": round_ratio(safe_divide(completed, len(items))),
                "risk_distribution": _risk_distribution(risk_counter, total_risk),
            }
        )
    return sorted(rows, key=lambda row: (row["commission_revenue_usd_equivalent"] or Decimal("0"), row["remittance_count"]), reverse=True)


def calculate_customers(db: Session, filters: BIFilters) -> dict:
    current = filtered_transactions(db, filters)
    active_sender_ids = {tx.sender_id for tx in current}
    first_by_sender: dict[int, datetime] = {}
    for tx in db.scalars(select(Transaction).order_by(Transaction.created_at)).all():
        first_by_sender.setdefault(tx.sender_id, tx.created_at)
    new_clients = 0
    returning_clients = 0
    for sender_id in active_sender_ids:
        first_date = first_by_sender.get(sender_id)
        if first_date and filters.date_from and first_date >= filters.date_from:
            new_clients += 1
        elif filters.date_from and first_date and first_date < filters.date_from:
            returning_clients += 1
        elif not filters.date_from:
            new_clients += 1
    per_client = Counter(tx.sender_id for tx in current)
    repeat_senders = sum(1 for count in per_client.values() if count > 1)
    total_amount = sum((money_to_usd(tx.source_amount, tx.source_currency) for tx in current), Decimal("0"))
    return {
        "active_clients": len(active_sender_ids),
        "new_clients": new_clients,
        "returning_clients": returning_clients,
        "repeat_senders": repeat_senders,
        "repeat_sender_rate": round_ratio(safe_divide(repeat_senders, len(active_sender_ids))),
        "remittances_per_client": round_ratio(safe_divide(len(current), len(active_sender_ids))),
        "average_amount_per_client_usd_equivalent": round_money(safe_divide(total_amount, len(active_sender_ids))),
    }


def calculate_operations(db: Session, filters: BIFilters) -> dict:
    transactions = filtered_transactions(db, filters)
    counts = Counter(tx.status for tx in transactions)
    return {
        "status_distribution": [
            {"status": status, "label": STATUS_LABELS.get(status, status), "count": count}
            for status, count in sorted(counts.items())
        ],
        "processing_remittances": counts.get("PROCESSING", 0),
        "available_remittances": counts.get("AVAILABLE", 0),
        "completed_remittances": counts.get("COMPLETED", 0),
        "review_required": counts.get("REVIEW_REQUIRED", 0),
        "rejected_remittances": counts.get("REJECTED", 0),
        "average_completion_time": None,
        "median_completion_time": None,
    }


def calculate_risk(db: Session, filters: BIFilters) -> dict:
    transactions = filtered_transactions(db, filters)
    transaction_ids = {tx.id for tx in transactions}
    assessments = [item for item in db.scalars(select(RiskAssessment)).all() if item.remittance_id in transaction_ids]
    bands = Counter(item.risk_band for item in assessments)
    reviews = Counter(item.review_decision for item in assessments if item.review_status == "REVIEWED")
    average_score = safe_divide(sum((Decimal(item.final_risk_score or 0) for item in assessments), Decimal("0")), len(assessments))
    total = len(assessments)
    return {
        "assessment_count": total,
        "risk_distribution": _risk_distribution(bands, total),
        "average_final_risk_score": round_ratio(average_score),
        "manual_reviews": sum(1 for item in assessments if item.recommended_action in {"REVIEW", "MANUAL_REVIEW"}),
        "review_count": sum(reviews.values()),
        "approved_reviews": reviews.get("APPROVE", 0),
        "escalated_reviews": reviews.get("ESCALATE", 0),
        "rejected_reviews": reviews.get("REJECT", 0),
    }


def _risk_counts_by_remittance(db: Session) -> dict[int, list[str]]:
    rows: dict[int, list[str]] = defaultdict(list)
    for assessment in db.scalars(select(RiskAssessment)).all():
        rows[assessment.remittance_id].append(assessment.risk_band)
    return rows


def _risk_distribution(counter: Counter, total: int) -> list[dict]:
    return [
        {
            "risk_band": band,
            "label": RISK_BAND_LABELS.get(band, band),
            "count": counter.get(band, 0),
            "share": round_ratio(safe_divide(counter.get(band, 0), total)),
        }
        for band in ["LOW", "MEDIUM", "HIGH"]
    ]


def _period_key(value: datetime, granularity: str) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    if granularity == "month":
        return value.strftime("%Y-%m")
    if granularity == "day":
        return value.strftime("%Y-%m-%d")
    start = value.date()
    week_start = start.fromordinal(start.toordinal() - start.weekday())
    return week_start.isoformat()
