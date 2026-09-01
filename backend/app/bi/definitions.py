from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


COMPLETED_STATUS = "COMPLETED"
BI_ELIGIBLE_STATUSES = {"AVAILABLE", "COMPLETED", "PROCESSING", "REVIEW_REQUIRED", "REJECTED"}
STATUS_LABELS = {
    "AVAILABLE": "Disponible",
    "COMPLETED": "Completada",
    "PROCESSING": "En proceso",
    "REVIEW_REQUIRED": "Revision requerida",
    "REJECTED": "Rechazada",
    "CREATED": "Creada",
}
RISK_BAND_LABELS = {"LOW": "Bajo", "MEDIUM": "Medio", "HIGH": "Alto"}


def round_money(value: Decimal | float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_ratio(value: Decimal | float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def safe_divide(numerator: Decimal | int | float, denominator: Decimal | int | float) -> Decimal | None:
    denominator_value = Decimal(str(denominator))
    if denominator_value == 0:
        return None
    return Decimal(str(numerator)) / denominator_value


def percent_change(current: Decimal | int | float, previous: Decimal | int | float) -> Decimal | None:
    previous_value = Decimal(str(previous))
    if previous_value == 0:
        return None
    return (Decimal(str(current)) - previous_value) / previous_value
