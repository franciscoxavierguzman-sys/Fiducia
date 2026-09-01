from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from app.analytics.constants import REQUIRED_FIELDS
from app.analytics.synthetic import write_synthetic_csv
from app.analytics.validation import validate_csv


def run_pipeline(
    records: int,
    seed: int,
    synthetic_path: Path,
    processed_path: Path,
    report_path: Path,
) -> dict[str, object]:
    if not synthetic_path.exists():
        write_synthetic_csv(synthetic_path, records=records, seed=seed)

    rows, report = validate_csv(synthetic_path)
    processed_rows = transform_records(rows)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_path.open("w", newline="", encoding="utf-8") as file:
        fieldnames = list(processed_rows[0].keys()) if processed_rows else REQUIRED_FIELDS
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    final_report = {
        **report,
        "synthetic_path": str(synthetic_path),
        "processed_path": str(processed_path),
        "records_requested": records,
        "seed": seed,
    }
    report_path.write_text(json.dumps(final_report, indent=2, ensure_ascii=False), encoding="utf-8")
    return final_report


def transform_records(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    transformed: list[dict[str, str]] = []
    for row in rows:
        source_amount = Decimal(row["source_amount"])
        historical_avg = Decimal(row["historical_avg_amount"])
        final_risk_score = Decimal(row["final_risk_score"])
        processed = dict(row)
        processed["amount_bucket"] = _amount_bucket(source_amount)
        processed["risk_band_experimental"] = _risk_band(final_risk_score)
        processed["amount_vs_user_average"] = str(_money(source_amount / historical_avg if historical_avg > 0 else Decimal("1")))
        processed["is_cross_border"] = str(int(row["origin_country"] != row["destination_country"]))
        transformed.append(processed)
    return transformed


def _amount_bucket(amount: Decimal) -> str:
    if amount < Decimal("100"):
        return "0-99"
    if amount < Decimal("500"):
        return "100-499"
    if amount < Decimal("1000"):
        return "500-999"
    if amount < Decimal("2500"):
        return "1000-2499"
    return "2500+"


def _risk_band(score: Decimal) -> str:
    if score < Decimal("30"):
        return "BAJO"
    if score < Decimal("60"):
        return "MEDIO"
    return "ALTO"


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

