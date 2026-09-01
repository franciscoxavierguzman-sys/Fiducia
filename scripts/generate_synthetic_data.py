from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.analytics.synthetic import write_synthetic_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera datos sinteticos reproducibles para FIDUCIA Fase 3.")
    parser.add_argument("--records", type=int, default=10000, help="Cantidad de remesas sinteticas.")
    parser.add_argument("--seed", type=int, default=42, help="Seed para reproducibilidad.")
    parser.add_argument("--fraud-rate", type=Decimal, default=Decimal("0.035"), help="Proporcion de fraude sintetico.")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "synthetic" / "remittances_synthetic.csv")
    args = parser.parse_args()

    if args.records <= 0:
        raise SystemExit("--records debe ser mayor a 0")
    if args.fraud_rate < 0 or args.fraud_rate > 1:
        raise SystemExit("--fraud-rate debe estar entre 0 y 1")

    rows = write_synthetic_csv(args.output, records=args.records, seed=args.seed, fraud_rate=args.fraud_rate)
    print(f"Dataset sintetico generado: {args.output}")
    print(f"Registros: {len(rows)} | Seed: {args.seed} | Fraude sintetico: {args.fraud_rate}")


if __name__ == "__main__":
    main()

