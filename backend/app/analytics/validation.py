from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.analytics.constants import COUNTRY_CURRENCIES, DELIVERY_METHODS, MONEY_FIELDS, PAYMENT_METHODS, REQUIRED_FIELDS, STATUSES


TOLERANCE = Decimal("0.02")


def validate_records(rows: list[dict[str, str]]) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_remittances: set[str] = set()
    valid_currencies = set(COUNTRY_CURRENCIES.values())

    for index, row in enumerate(rows, start=2):
        missing = [field for field in REQUIRED_FIELDS if row.get(field) in {None, ""}]
        if missing:
            errors.append(f"Fila {index}: campos obligatorios vacios: {', '.join(missing)}")

        remittance_id = row.get("remittance_id", "")
        if remittance_id in seen_remittances:
            errors.append(f"Fila {index}: remittance_id duplicado {remittance_id}")
        seen_remittances.add(remittance_id)

        origin_country = row.get("origin_country", "")
        destination_country = row.get("destination_country", "")
        if origin_country == destination_country:
            errors.append(f"Fila {index}: origin_country no puede ser igual a destination_country")
        if origin_country not in COUNTRY_CURRENCIES:
            errors.append(f"Fila {index}: pais origen invalido {origin_country}")
        if destination_country not in COUNTRY_CURRENCIES:
            errors.append(f"Fila {index}: pais destino invalido {destination_country}")
        if row.get("source_currency") not in valid_currencies:
            errors.append(f"Fila {index}: source_currency invalida {row.get('source_currency')}")
        if row.get("destination_currency") not in valid_currencies:
            errors.append(f"Fila {index}: destination_currency invalida {row.get('destination_currency')}")
        if origin_country in COUNTRY_CURRENCIES and row.get("source_currency") != COUNTRY_CURRENCIES[origin_country]:
            errors.append(f"Fila {index}: source_currency no corresponde al pais origen")
        if destination_country in COUNTRY_CURRENCIES and row.get("destination_currency") != COUNTRY_CURRENCIES[destination_country]:
            errors.append(f"Fila {index}: destination_currency no corresponde al pais destino")
        if row.get("status") not in STATUSES:
            errors.append(f"Fila {index}: estado invalido {row.get('status')}")
        if row.get("funding_method") not in PAYMENT_METHODS:
            errors.append(f"Fila {index}: metodo de fondeo invalido {row.get('funding_method')}")
        if row.get("delivery_method") not in DELIVERY_METHODS:
            errors.append(f"Fila {index}: metodo de entrega invalido {row.get('delivery_method')}")

        decimals = {field: _decimal(row.get(field, ""), index, field, errors) for field in MONEY_FIELDS if row.get(field, "") != ""}
        for field, value in decimals.items():
            if value is not None and field not in {"ml_probability", "anomaly_score"} and value < 0:
                errors.append(f"Fila {index}: {field} no puede ser negativo")
        if decimals.get("exchange_rate") is not None and decimals["exchange_rate"] <= 0:
            errors.append(f"Fila {index}: exchange_rate debe ser mayor a cero")

        source_amount = decimals.get("source_amount")
        commission_rate = decimals.get("commission_rate")
        commission_amount = decimals.get("commission_amount")
        total_debit_amount = decimals.get("total_debit_amount")
        exchange_rate = decimals.get("exchange_rate")
        destination_amount = decimals.get("destination_amount")
        if source_amount is not None and commission_rate is not None and commission_amount is not None:
            expected = (source_amount * commission_rate).quantize(Decimal("0.01"))
            if abs(expected - commission_amount) > TOLERANCE:
                errors.append(f"Fila {index}: commission_amount esperado {expected}, recibido {commission_amount}")
        if source_amount is not None and commission_amount is not None and total_debit_amount is not None:
            expected = (source_amount + commission_amount).quantize(Decimal("0.01"))
            if abs(expected - total_debit_amount) > TOLERANCE:
                errors.append(f"Fila {index}: total_debit_amount esperado {expected}, recibido {total_debit_amount}")
        if source_amount is not None and exchange_rate is not None and destination_amount is not None:
            expected = (source_amount * exchange_rate).quantize(Decimal("0.01"))
            if abs(expected - destination_amount) > TOLERANCE:
                errors.append(f"Fila {index}: destination_amount esperado {expected}, recibido {destination_amount}")

        _parse_date(row.get("registration_date", ""), index, "registration_date", errors)
        created_at = _parse_datetime(row.get("created_at", ""), index, "created_at", errors)
        completed_at = row.get("completed_at", "")
        if completed_at:
            completed = _parse_datetime(completed_at, index, "completed_at", errors)
            if created_at and completed and completed < created_at:
                errors.append(f"Fila {index}: completed_at no puede ser anterior a created_at")

    fraud_count = sum(1 for row in rows if row.get("fraud_label") == "1")
    if rows and fraud_count == 0:
        warnings.append("No hay casos con fraud_label=1; el dataset pierde utilidad para experimentacion futura.")

    return {
        "record_count": len(rows),
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:200],
        "warnings": warnings,
        "fraud_label_count": fraud_count,
    }


def validate_csv(path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    import csv

    with path.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return rows, validate_records(rows)


def _decimal(raw: str, row: int, field: str, errors: list[str]) -> Decimal | None:
    try:
        return Decimal(str(raw))
    except (InvalidOperation, ValueError):
        errors.append(f"Fila {row}: {field} no es Decimal valido")
        return None


def _parse_datetime(raw: str, row: int, field: str, errors: list[str]) -> datetime | None:
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        errors.append(f"Fila {row}: {field} no tiene formato ISO valido")
        return None


def _parse_date(raw: str, row: int, field: str, errors: list[str]) -> None:
    try:
        datetime.fromisoformat(raw)
    except ValueError:
        errors.append(f"Fila {row}: {field} no tiene formato de fecha valido")

