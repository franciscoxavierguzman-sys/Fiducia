from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / "reports" / "forecasting" / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.forecasting.audit import temporal_audit
from app.forecasting.preprocessing import PROCESSED_DATASET_PATH, build_weekly_series, load_remittance_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=PROCESSED_DATASET_PATH)
    args = parser.parse_args()
    report_dir = PROJECT_ROOT / "reports" / "forecasting"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = temporal_audit(args.source)
    (report_dir / "temporal_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    data = load_remittance_dataset(args.source)
    weekly = build_weekly_series(data)
    save_plots(data, weekly, report_dir)
    print(json.dumps({"go_decision": report["go_decision"], "weeks_covered": report["weeks_covered"], "months_covered": report["months_covered"]}, indent=2))


def save_plots(data, weekly, report_dir: Path) -> None:
    plt.figure(figsize=(10, 4))
    data.set_index("created_at").resample("D").size().plot()
    plt.title("Distribucion diaria de remesas")
    plt.tight_layout()
    plt.savefig(report_dir / "temporal_distribution.png")
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(weekly["period"], weekly["transaction_count"], label="Remesas semanales")
    plt.title("Tendencia semanal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(report_dir / "trend.png")
    plt.close()

    weekday = data["created_at"].dt.day_name().value_counts()
    plt.figure(figsize=(8, 4))
    weekday.plot(kind="bar")
    plt.title("Estacionalidad por dia de semana")
    plt.tight_layout()
    plt.savefig(report_dir / "seasonality.png")
    plt.close()

    values = weekly["transaction_count"].to_numpy()
    autocorr = [1.0 if lag == 0 else float(weekly["transaction_count"].autocorr(lag=lag)) for lag in range(0, min(16, len(values) - 1))]
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(autocorr)), autocorr)
    plt.title("Autocorrelacion semanal")
    plt.tight_layout()
    plt.savefig(report_dir / "autocorrelation.png")
    plt.close()


if __name__ == "__main__":
    main()
