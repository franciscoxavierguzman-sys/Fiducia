from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ml.training.train import train_fraud_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena modelos de fraude para FIDUCIA Fase 4.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "processed" / "remittances_analytics.csv")
    parser.add_argument("--artifact-dir", type=Path, default=ROOT / "ml" / "artifacts")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports" / "ml")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = train_fraud_model(args.dataset, args.artifact_dir, args.report_dir, args.seed)
    metadata = result["metadata"]
    print(f"Modelo seleccionado: {metadata['selected_model']} ({metadata['algorithm']})")
    print(f"Version: {metadata['model_version']} | Threshold: {metadata['threshold']}")
    print(f"Artefacto: {result['artifact_path']}")


if __name__ == "__main__":
    main()

