from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
metrics_path = ROOT / "ml" / "artifacts" / "model_metrics.json"
metadata_path = ROOT / "ml" / "artifacts" / "model_metadata.json"

if not metrics_path.exists() or not metadata_path.exists():
    raise SystemExit("Primero ejecuta scripts/train_fraud_model.py")

metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
print(f"Modelo activo: {metadata['selected_model']} | Version: {metadata['model_version']}")
for item in metrics["comparison"]:
    test = item["test"]
    print(
        f"{item['model']}: precision={test['precision']:.4f} recall={test['recall']:.4f} "
        f"f1={test['f1']:.4f} roc_auc={test['roc_auc']:.4f} pr_auc={test['pr_auc']:.4f} "
        f"threshold={item['threshold']}"
    )
