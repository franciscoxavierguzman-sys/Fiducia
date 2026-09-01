from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP


def summarize_records(rows: list[dict[str, str]]) -> dict[str, object]:
    total = len(rows)
    total_volume = sum((Decimal(row["source_amount"]) for row in rows), Decimal("0"))
    total_commission = sum((Decimal(row["commission_amount"]) for row in rows), Decimal("0"))
    average_amount = total_volume / Decimal(total) if total else Decimal("0")
    status_distribution = Counter(row["status"] for row in rows)
    top_corridors = Counter(f"{row['origin_country']} -> {row['destination_country']}" for row in rows)
    fraud_count = sum(1 for row in rows if row.get("fraud_label") == "1")

    return {
        "total_remittances": total,
        "total_volume": str(_money(total_volume)),
        "total_commission": str(_money(total_commission)),
        "average_amount": str(_money(average_amount)),
        "top_corridor": top_corridors.most_common(1)[0][0] if top_corridors else None,
        "status_distribution": dict(status_distribution),
        "top_corridors": dict(top_corridors.most_common(10)),
        "origin_countries": dict(Counter(row["origin_country"] for row in rows)),
        "destination_countries": dict(Counter(row["destination_country"] for row in rows)),
        "currencies": dict(Counter(row["source_currency"] for row in rows)),
        "funding_methods": dict(Counter(row["funding_method"] for row in rows)),
        "delivery_methods": dict(Counter(row["delivery_method"] for row in rows)),
        "fraud_label_count": fraud_count,
        "fraud_label_rate": str(_rate(Decimal(fraud_count) / Decimal(total))) if total else "0.000000",
        "over_time": _over_time(rows),
    }


def _over_time(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, Decimal] = defaultdict(Decimal)
    counts: Counter[str] = Counter()
    for row in rows:
        period = row["created_at"][:7]
        grouped[period] += Decimal(row["source_amount"])
        counts[period] += 1
    return [
        {"period": period, "count": str(counts[period]), "volume": str(_money(grouped[period]))}
        for period in sorted(grouped)
    ]


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _rate(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
