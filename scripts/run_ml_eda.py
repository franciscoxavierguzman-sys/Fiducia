from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.evaluation.eda import run_eda


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta EDA reproducible para FIDUCIA Fase 4.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "processed" / "remittances_analytics.csv")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports" / "ml")
    args = parser.parse_args()
    report = run_eda(args.dataset, args.report_dir)
    print(f"EDA generado en {args.report_dir}")
    print(f"Registros: {report['records']} | Target: {report['target_distribution']}")


if __name__ == "__main__":
    main()

