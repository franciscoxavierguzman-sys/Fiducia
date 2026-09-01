from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any


def normalize_for_canonical(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value.quantize(Decimal("0.000001")).normalize(), "f")
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return format(Decimal(str(value)).quantize(Decimal("0.000001")).normalize(), "f")
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): normalize_for_canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [normalize_for_canonical(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_for_canonical(item) for item in value]
    return value


def canonical_json(payload: dict[str, Any]) -> str:
    normalized = normalize_for_canonical(payload)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
