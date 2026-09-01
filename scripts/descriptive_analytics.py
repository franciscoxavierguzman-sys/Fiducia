from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.analytics.descriptive import summarize_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera analitica descriptiva sobre el dataset procesado.")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "processed" / "remittances_analytics.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "descriptive_summary.json")
    args = parser.parse_args()

    with args.input.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    summary = summarize_records(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Resumen descriptivo generado: {args.output}")


if __name__ == "__main__":
    main()
