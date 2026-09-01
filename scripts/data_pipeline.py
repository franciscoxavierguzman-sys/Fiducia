from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.analytics.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline analitico FIDUCIA Fase 3.")
    parser.add_argument("--records", type=int, default=10000, help="Registros a generar si no existe dataset sintetico.")
    parser.add_argument("--seed", type=int, default=42, help="Seed para generacion reproducible.")
    parser.add_argument("--synthetic-input", type=Path, default=ROOT / "data" / "synthetic" / "remittances_synthetic.csv")
    parser.add_argument("--processed-output", type=Path, default=ROOT / "data" / "processed" / "remittances_analytics.csv")
    parser.add_argument("--report-output", type=Path, default=ROOT / "data" / "processed" / "validation_report.json")
    args = parser.parse_args()

    report = run_pipeline(
        records=args.records,
        seed=args.seed,
        synthetic_path=args.synthetic_input,
        processed_path=args.processed_output,
        report_path=args.report_output,
    )
    print(f"Pipeline completado. Valido: {report['valid']}")
    print(f"Registros: {report['record_count']} | Errores: {report['error_count']} | Advertencias: {report['warning_count']}")
    print(f"Dataset procesado: {args.processed_output}")
    print(f"Reporte: {args.report_output}")


if __name__ == "__main__":
    main()

