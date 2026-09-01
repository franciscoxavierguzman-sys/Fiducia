from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.forecasting import generate_forecast


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["transaction_count", "transaction_amount_usd"], default="transaction_count")
    parser.add_argument("--horizon", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(generate_forecast(args.target, args.horizon), indent=2, ensure_ascii=False, default=serialize))


def serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


if __name__ == "__main__":
    main()
