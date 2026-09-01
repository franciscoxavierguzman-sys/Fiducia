from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.bi.calculations import calculate_overview
from app.bi.definitions import percent_change, round_money, round_ratio
from app.bi.filters import BIFilters, previous_period


def compare_overview(db: Session, filters: BIFilters) -> dict:
    current = calculate_overview(db, filters)
    previous_filters = previous_period(filters)
    if previous_filters is None:
        return {"current": current, "previous": None, "changes": {}}
    previous = calculate_overview(db, previous_filters)
    changes = {}
    for key, current_value in current.items():
        previous_value = previous.get(key)
        if isinstance(current_value, int):
            absolute = current_value - int(previous_value or 0)
            change = percent_change(current_value, previous_value or 0)
            changes[key] = {"absolute_change": absolute, "percentage_change": round_ratio(change)}
        else:
            current_decimal = Decimal(str(current_value or 0))
            previous_decimal = Decimal(str(previous_value or 0))
            change = percent_change(current_decimal, previous_decimal)
            changes[key] = {"absolute_change": round_money(current_decimal - previous_decimal), "percentage_change": round_ratio(change)}
    return {"current": current, "previous": previous, "changes": changes}
