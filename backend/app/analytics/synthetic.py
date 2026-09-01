from __future__ import annotations

import csv
import random
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from app.analytics.constants import COUNTRY_CURRENCIES, DELIVERY_METHODS, EXCHANGE_RATES_TO_USD, PAYMENT_METHODS, REQUIRED_FIELDS


MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.000001")


@dataclass(frozen=True)
class SyntheticUser:
    user_id: str
    country: str
    registration_date: datetime
    preferred_destinations: tuple[str, ...]


@dataclass(frozen=True)
class SyntheticBeneficiary:
    beneficiary_id: str
    user_id: str
    relationship: str
    destination_country: str
    created_at: datetime
    linked_user: int


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def rate(value: Decimal) -> Decimal:
    return value.quantize(RATE_QUANT, rounding=ROUND_HALF_UP)


def exchange_rate(source_currency: str, destination_currency: str) -> Decimal:
    source_to_usd = EXCHANGE_RATES_TO_USD[source_currency]
    destination_to_usd = EXCHANGE_RATES_TO_USD[destination_currency]
    return rate(source_to_usd / destination_to_usd)


def generate_synthetic_records(records: int = 10000, seed: int = 42, fraud_rate: Decimal = Decimal("0.035")) -> list[dict[str, str]]:
    rng = random.Random(seed)
    user_count = max(80, min(1200, records // 8))
    now = datetime(2026, 8, 28, tzinfo=UTC)
    start_date = now - timedelta(days=540)
    users = _build_users(rng, user_count, start_date, now)
    beneficiaries = _build_beneficiaries(rng, users, start_date, now)
    rows: list[dict[str, str]] = []
    user_amounts: dict[str, list[Decimal]] = defaultdict(list)
    user_times: dict[str, deque[datetime]] = defaultdict(deque)
    user_destinations_30d: dict[str, deque[tuple[datetime, str]]] = defaultdict(deque)
    user_failed: dict[str, int] = defaultdict(int)
    user_corridors: dict[str, set[str]] = defaultdict(set)

    for index in range(1, records + 1):
        user = rng.choice(users)
        available_beneficiaries = [item for item in beneficiaries if item.user_id == user.user_id]
        beneficiary = rng.choice(available_beneficiaries)
        origin_country = user.country
        destination_country = beneficiary.destination_country
        if origin_country == destination_country:
            destination_country = rng.choice([country for country in COUNTRY_CURRENCIES if country != origin_country])
        source_currency = COUNTRY_CURRENCIES[origin_country]
        destination_currency = COUNTRY_CURRENCIES[destination_country]
        created_at = start_date + timedelta(seconds=rng.randint(0, int((now - start_date).total_seconds())))
        created_at = _biased_transaction_time(rng, created_at)
        is_synthetic_fraud = rng.random() < float(fraud_rate)
        source_amount = _amount_for_user(rng, user_amounts[user.user_id], is_synthetic_fraud)
        commission_rate = rate(Decimal("0.018") + Decimal(str(rng.random())) * Decimal("0.018"))
        commission_amount = money(source_amount * commission_rate)
        total_debit_amount = money(source_amount + commission_amount)
        fx = exchange_rate(source_currency, destination_currency)
        destination_amount = money(source_amount * fx)

        _discard_old_events(user_times[user.user_id], created_at, hours=24)
        tx_last_24h = len(user_times[user.user_id])
        tx_last_7d = _count_recent(user_times[user.user_id], created_at, days=7)
        tx_last_30d = _count_recent(user_times[user.user_id], created_at, days=30)
        _discard_old_country_events(user_destinations_30d[user.user_id], created_at, days=30)
        countries_last_30d = {country for _, country in user_destinations_30d[user.user_id]}
        prior_amounts = user_amounts[user.user_id]
        historical_avg = money(sum(prior_amounts, Decimal("0")) / len(prior_amounts)) if prior_amounts else source_amount
        historical_max = max(prior_amounts) if prior_amounts else source_amount
        amount_vs_average = money(source_amount / historical_avg) if historical_avg > 0 else Decimal("1.00")
        beneficiary_age_days = max(0, (created_at.date() - beneficiary.created_at.date()).days)
        corridor_key = f"{origin_country}->{destination_country}"
        new_corridor = 1 if corridor_key not in user_corridors[user.user_id] else 0
        unusual_hour = 1 if created_at.hour <= 5 else 0
        weekend = 1 if created_at.weekday() >= 5 else 0
        failed_ratio = Decimal(user_failed[user.user_id]) / Decimal(max(1, len(prior_amounts)))

        risk_basis = (
            Decimal("18") * Decimal(is_synthetic_fraud)
            + Decimal("8") * Decimal(tx_last_24h >= 3)
            + Decimal("7") * Decimal(beneficiary_age_days <= 3)
            + Decimal("6") * Decimal(unusual_hour)
            + Decimal("5") * Decimal(new_corridor)
            + Decimal("4") * Decimal(amount_vs_average >= Decimal("2.0"))
        )
        rule_score = min(Decimal("99.00"), money(risk_basis + Decimal(str(rng.uniform(4, 18)))))
        ml_probability = rate(min(Decimal("0.950000"), Decimal("0.050000") + (rule_score / Decimal("140"))))
        anomaly_score = rate(min(Decimal("1.000000"), Decimal(str(rng.random())) * Decimal("0.35") + (rule_score / Decimal("120"))))
        final_risk_score = min(Decimal("99.00"), money((rule_score * Decimal("0.65")) + (anomaly_score * Decimal("35"))))
        status = _status_for_record(rng, is_synthetic_fraud)
        if status in {"REJECTED", "REVIEW_REQUIRED"}:
            user_failed[user.user_id] += 1

        row = {
            "user_id": user.user_id,
            "country": user.country,
            "account_age_days": str((created_at.date() - user.registration_date.date()).days),
            "transaction_count": str(len(prior_amounts)),
            "historical_amount": str(money(sum(prior_amounts, Decimal("0")))),
            "registration_date": user.registration_date.date().isoformat(),
            "remittance_id": f"REM-{seed}-{index:07d}",
            "remittance_number": f"FID-2026-{index:06d}",
            "origin_country": origin_country,
            "destination_country": destination_country,
            "source_currency": source_currency,
            "destination_currency": destination_currency,
            "source_amount": str(source_amount),
            "commission_rate": str(commission_rate),
            "commission_amount": str(commission_amount),
            "total_debit_amount": str(total_debit_amount),
            "exchange_rate": str(fx),
            "destination_amount": str(destination_amount),
            "delivery_method": rng.choice(tuple(DELIVERY_METHODS)),
            "funding_method": rng.choice(tuple(PAYMENT_METHODS)),
            "status": status,
            "created_at": created_at.isoformat(),
            "completed_at": (created_at + timedelta(minutes=rng.randint(5, 720))).isoformat() if status == "COMPLETED" else "",
            "beneficiary_id": beneficiary.beneficiary_id,
            "relationship": beneficiary.relationship,
            "linked_user": str(beneficiary.linked_user),
            "transactions_last_24h": str(tx_last_24h),
            "transactions_last_7d": str(tx_last_7d),
            "transactions_last_30d": str(tx_last_30d),
            "avg_transaction_amount": str(historical_avg),
            "max_transaction_amount": str(historical_max),
            "new_beneficiary": str(int(beneficiary_age_days <= 7)),
            "beneficiary_age_days": str(beneficiary_age_days),
            "countries_used_last_30d": str(len(countries_last_30d)),
            "failed_transactions": str(user_failed[user.user_id]),
            "transaction_hour": str(created_at.hour),
            "weekend_transaction": str(weekend),
            "amount_vs_user_average": str(amount_vs_average),
            "transaction_velocity_24h": str(tx_last_24h),
            "transaction_velocity_7d": str(tx_last_7d),
            "new_beneficiary_flag": str(int(beneficiary_age_days <= 7)),
            "unusual_hour_flag": str(unusual_hour),
            "weekend_flag": str(weekend),
            "new_corridor_flag": str(new_corridor),
            "country_diversity_30d": str(len(countries_last_30d)),
            "failed_transaction_ratio": str(rate(failed_ratio)),
            "historical_avg_amount": str(historical_avg),
            "historical_max_amount": str(historical_max),
            "rule_score": str(rule_score),
            "ml_probability": str(ml_probability),
            "anomaly_score": str(anomaly_score),
            "final_risk_score": str(final_risk_score),
            "fraud_label": str(int(is_synthetic_fraud)),
        }
        rows.append(row)
        user_amounts[user.user_id].append(source_amount)
        user_times[user.user_id].append(created_at)
        user_destinations_30d[user.user_id].append((created_at, destination_country))
        user_corridors[user.user_id].add(corridor_key)

    return rows


def write_synthetic_csv(path: Path, records: int = 10000, seed: int = 42, fraud_rate: Decimal = Decimal("0.035")) -> list[dict[str, str]]:
    rows = generate_synthetic_records(records=records, seed=seed, fraud_rate=fraud_rate)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[*REQUIRED_FIELDS[:23], "completed_at", *REQUIRED_FIELDS[23:]])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _build_users(rng: random.Random, user_count: int, start_date: datetime, now: datetime) -> list[SyntheticUser]:
    countries = list(COUNTRY_CURRENCIES)
    users: list[SyntheticUser] = []
    for index in range(1, user_count + 1):
        country = rng.choices(countries, weights=[32, 34, 9, 16, 9], k=1)[0]
        registration_date = start_date + timedelta(days=rng.randint(0, 480))
        destinations = tuple(rng.sample([item for item in countries if item != country], k=rng.randint(1, 3)))
        users.append(SyntheticUser(f"USR-{index:06d}", country, registration_date, destinations))
    return users


def _build_beneficiaries(
    rng: random.Random, users: list[SyntheticUser], start_date: datetime, now: datetime
) -> list[SyntheticBeneficiary]:
    relationships = ["Padre / Madre", "Hijo / Hija", "Hermano / Hermana", "Conyuge", "Amigo / Amiga", "Socio comercial"]
    beneficiaries: list[SyntheticBeneficiary] = []
    counter = 1
    for user in users:
        for _ in range(rng.randint(1, 4)):
            destination = rng.choice(user.preferred_destinations)
            created_at = start_date + timedelta(days=rng.randint(0, 500))
            beneficiaries.append(
                SyntheticBeneficiary(
                    beneficiary_id=f"BEN-{counter:06d}",
                    user_id=user.user_id,
                    relationship=rng.choice(relationships),
                    destination_country=destination,
                    created_at=created_at,
                    linked_user=rng.choices([0, 1], weights=[72, 28], k=1)[0],
                )
            )
            counter += 1
    return beneficiaries


def _biased_transaction_time(rng: random.Random, created_at: datetime) -> datetime:
    if rng.random() < 0.72:
        return created_at.replace(hour=rng.randint(8, 21), minute=rng.randint(0, 59), second=rng.randint(0, 59))
    return created_at.replace(hour=rng.choice([0, 1, 2, 3, 4, 5, 22, 23]), minute=rng.randint(0, 59), second=rng.randint(0, 59))


def _amount_for_user(rng: random.Random, prior_amounts: list[Decimal], is_synthetic_fraud: bool) -> Decimal:
    base = Decimal(str(rng.lognormvariate(5.55, 0.72)))
    if is_synthetic_fraud and prior_amounts and rng.random() < 0.55:
        base = max(prior_amounts) * Decimal(str(rng.uniform(1.8, 3.8)))
    return money(min(Decimal("5000.00"), max(Decimal("10.00"), base)))


def _status_for_record(rng: random.Random, is_synthetic_fraud: bool) -> str:
    if is_synthetic_fraud:
        return rng.choices(
            ["COMPLETED", "AVAILABLE", "PROCESSING", "REVIEW_REQUIRED", "REJECTED"],
            weights=[28, 18, 16, 25, 13],
            k=1,
        )[0]
    return rng.choices(
        ["COMPLETED", "AVAILABLE", "PROCESSING", "REVIEW_REQUIRED", "REJECTED"],
        weights=[70, 16, 9, 4, 1],
        k=1,
    )[0]


def _discard_old_events(events: deque[datetime], current: datetime, hours: int) -> None:
    cutoff = current - timedelta(hours=hours)
    while events and events[0] < cutoff:
        events.popleft()


def _discard_old_country_events(events: deque[tuple[datetime, str]], current: datetime, days: int) -> None:
    cutoff = current - timedelta(days=days)
    while events and events[0][0] < cutoff:
        events.popleft()


def _count_recent(events: deque[datetime], current: datetime, days: int) -> int:
    cutoff = current - timedelta(days=days)
    return sum(1 for item in events if item >= cutoff)

