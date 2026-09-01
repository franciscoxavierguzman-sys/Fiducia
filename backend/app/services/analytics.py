from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.constants import EXCHANGE_RATES_TO_USD
from app.models.transaction import Transaction
from app.schemas.analytics import AnalyticsDistributionItem, AnalyticsSummary, AnalyticsTimeSeriesPoint


MONEY_QUANT = Decimal("0.01")


def get_analytics_summary(db: Session) -> AnalyticsSummary:
    transactions = _list_transactions(db)
    volume = sum((_to_usd(tx.source_amount, tx.source_currency) for tx in transactions), Decimal("0"))
    commission = sum((_to_usd(tx.commission_amount, tx.source_currency) for tx in transactions), Decimal("0"))
    top_corridor = Counter(_corridor(tx) for tx in transactions).most_common(1)
    synthetic_fraud_cases = sum(1 for tx in transactions if tx.risk_level == "SYNTHETIC_FRAUD")
    return AnalyticsSummary(
        total_remittances=len(transactions),
        volume_usd_equivalent=_money(volume),
        commission_usd_equivalent=_money(commission),
        average_ticket_usd_equivalent=_money(volume / Decimal(len(transactions))) if transactions else Decimal("0.00"),
        top_corridor=top_corridor[0][0] if top_corridor else None,
        synthetic_fraud_cases=synthetic_fraud_cases,
    )


def get_remittances_over_time(db: Session) -> list[AnalyticsTimeSeriesPoint]:
    grouped: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"count": 0, "volume": Decimal("0"), "commission": Decimal("0")}
    )
    for tx in _list_transactions(db):
        period = tx.created_at.strftime("%Y-%m")
        grouped[period]["count"] += 1
        grouped[period]["volume"] += _to_usd(tx.source_amount, tx.source_currency)
        grouped[period]["commission"] += _to_usd(tx.commission_amount, tx.source_currency)
    return [
        AnalyticsTimeSeriesPoint(
            period=period,
            count=int(values["count"]),
            volume_usd_equivalent=_money(Decimal(values["volume"])),
            commission_usd_equivalent=_money(Decimal(values["commission"])),
        )
        for period, values in sorted(grouped.items())
    ]


def get_top_corridors(db: Session, limit: int = 8) -> list[AnalyticsDistributionItem]:
    counters: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"count": 0, "amount": Decimal("0")})
    for tx in _list_transactions(db):
        key = _corridor(tx)
        counters[key]["count"] += 1
        counters[key]["amount"] += _to_usd(tx.source_amount, tx.source_currency)
    items = sorted(counters.items(), key=lambda item: (item[1]["count"], item[1]["amount"]), reverse=True)
    return [
        AnalyticsDistributionItem(label=label, count=int(values["count"]), amount=_money(Decimal(values["amount"])), currency="USD")
        for label, values in items[:limit]
    ]


def get_status_distribution(db: Session) -> list[AnalyticsDistributionItem]:
    counts = Counter(tx.status for tx in _list_transactions(db))
    return [AnalyticsDistributionItem(label=status, count=count) for status, count in counts.most_common()]


def get_currency_distribution(db: Session) -> list[AnalyticsDistributionItem]:
    counts: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"count": 0, "amount": Decimal("0")})
    for tx in _list_transactions(db):
        counts[tx.source_currency]["count"] += 1
        counts[tx.source_currency]["amount"] += tx.source_amount
    return [
        AnalyticsDistributionItem(label=currency, count=int(values["count"]), amount=_money(Decimal(values["amount"])), currency=currency)
        for currency, values in sorted(counts.items())
    ]


def get_method_distribution(db: Session) -> dict[str, list[AnalyticsDistributionItem]]:
    funding = Counter(tx.payment_method for tx in _list_transactions(db))
    delivery = Counter(tx.delivery_method for tx in _list_transactions(db))
    return {
        "funding_methods": [AnalyticsDistributionItem(label=label, count=count) for label, count in funding.most_common()],
        "delivery_methods": [AnalyticsDistributionItem(label=label, count=count) for label, count in delivery.most_common()],
    }


def _list_transactions(db: Session) -> list[Transaction]:
    return list(db.scalars(select(Transaction).order_by(Transaction.created_at.asc(), Transaction.id.asc())).all())


def _to_usd(amount: Decimal, currency: str) -> Decimal:
    return Decimal(amount) * EXCHANGE_RATES_TO_USD.get(currency, Decimal("1"))


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _corridor(tx: Transaction) -> str:
    return f"{tx.origin_country} -> {tx.destination_country}"

