from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Select

from app.models.transaction import Transaction


@dataclass(frozen=True)
class BIFilters:
    date_from: datetime | None = None
    date_to: datetime | None = None
    origin_country: str | None = None
    destination_country: str | None = None
    currency: str | None = None
    status: str | None = None


def validate_filters(filters: BIFilters) -> None:
    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_DATE_RANGE", "message": "date_from debe ser menor o igual que date_to"},
        )


def apply_transaction_filters(statement: Select, filters: BIFilters) -> Select:
    validate_filters(filters)
    if filters.date_from:
        statement = statement.where(Transaction.created_at >= filters.date_from)
    if filters.date_to:
        statement = statement.where(Transaction.created_at <= filters.date_to)
    if filters.origin_country:
        statement = statement.where(Transaction.origin_country == filters.origin_country)
    if filters.destination_country:
        statement = statement.where(Transaction.destination_country == filters.destination_country)
    if filters.currency:
        statement = statement.where(Transaction.source_currency == filters.currency)
    if filters.status:
        statement = statement.where(Transaction.status == filters.status)
    return statement


def previous_period(filters: BIFilters) -> BIFilters | None:
    if not filters.date_from or not filters.date_to:
        return None
    delta = filters.date_to - filters.date_from
    previous_to = filters.date_from
    previous_from = filters.date_from - delta
    return BIFilters(
        date_from=previous_from,
        date_to=previous_to,
        origin_country=filters.origin_country,
        destination_country=filters.destination_country,
        currency=filters.currency,
        status=filters.status,
    )
