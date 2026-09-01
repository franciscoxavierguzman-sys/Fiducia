from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / "reports" / "ml" / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from ml.config import DATASET_PATH, REPORT_DIR, TARGET


def run_eda(dataset_path: Path = DATASET_PATH, report_dir: Path = REPORT_DIR) -> dict[str, object]:
    report_dir.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(dataset_path)
    target_distribution = data[TARGET].value_counts(normalize=False).sort_index().astype(int).to_dict()
    target_rate = data[TARGET].value_counts(normalize=True).sort_index().round(6).to_dict()
    numeric_summary = data[
        [
            "source_amount",
            "destination_amount",
            "commission_amount",
            "transaction_hour",
            "beneficiary_age_days",
            "transaction_velocity_24h",
            "transaction_velocity_7d",
            "amount_vs_user_average",
        ]
    ].describe().round(4).to_dict()
    by_target = data.groupby(TARGET)[
        ["source_amount", "destination_amount", "commission_amount", "beneficiary_age_days", "transaction_velocity_24h"]
    ].mean().round(4).to_dict()

    report = {
        "records": int(len(data)),
        "target_distribution": target_distribution,
        "target_rate": target_rate,
        "numeric_summary": numeric_summary,
        "means_by_target": by_target,
        "top_corridors": data.assign(corridor=data["origin_country"] + " -> " + data["destination_country"])["corridor"]
        .value_counts()
        .head(10)
        .astype(int)
        .to_dict(),
        "funding_methods": data["funding_method"].value_counts().astype(int).to_dict(),
        "delivery_methods": data["delivery_method"].value_counts().astype(int).to_dict(),
        "currencies": data["source_currency"].value_counts().astype(int).to_dict(),
    }
    (report_dir / "eda_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    _plot_target_distribution(data, report_dir)
    _plot_amount_distribution(data, report_dir)
    _plot_hour_distribution(data, report_dir)
    return report


def _plot_target_distribution(data: pd.DataFrame, report_dir: Path) -> None:
    counts = data[TARGET].value_counts().sort_index()
    plt.figure(figsize=(6, 4))
    counts.plot(kind="bar", color=["#0f766e", "#f97316"])
    plt.title("Distribucion de fraud_label")
    plt.xlabel("fraud_label")
    plt.ylabel("Registros")
    plt.tight_layout()
    plt.savefig(report_dir / "target_distribution.png")
    plt.close()


def _plot_amount_distribution(data: pd.DataFrame, report_dir: Path) -> None:
    plt.figure(figsize=(7, 4))
    data.boxplot(column="source_amount", by=TARGET)
    plt.title("Source amount por fraud_label")
    plt.suptitle("")
    plt.xlabel("fraud_label")
    plt.ylabel("source_amount")
    plt.tight_layout()
    plt.savefig(report_dir / "amount_by_target.png")
    plt.close()


def _plot_hour_distribution(data: pd.DataFrame, report_dir: Path) -> None:
    grouped = data.groupby([TARGET, "transaction_hour"]).size().unstack(0).fillna(0)
    plt.figure(figsize=(8, 4))
    grouped.plot(kind="line", ax=plt.gca())
    plt.title("Operaciones por hora")
    plt.xlabel("Hora")
    plt.ylabel("Registros")
    plt.tight_layout()
    plt.savefig(report_dir / "transactions_by_hour.png")
    plt.close()
