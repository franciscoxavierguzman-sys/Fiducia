from __future__ import annotations

from time import perf_counter

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_probabilities(y_true, probabilities, threshold: float) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(int)
    return {
        "precision": _safe_metric(precision_score, y_true, predictions, zero_division=0),
        "recall": _safe_metric(recall_score, y_true, predictions, zero_division=0),
        "f1": _safe_metric(f1_score, y_true, predictions, zero_division=0),
        "roc_auc": _safe_metric(roc_auc_score, y_true, probabilities),
        "pr_auc": _safe_metric(average_precision_score, y_true, probabilities),
        "brier_score": _safe_metric(brier_score_loss, y_true, probabilities),
        "threshold": threshold,
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
    }


def find_threshold(y_true, probabilities) -> dict[str, float]:
    candidates = np.arange(0.10, 0.91, 0.05)
    best_with_recall = {"threshold": 0.50, "f1": -1.0, "precision": 0.0, "recall": 0.0}
    best_overall = {"threshold": 0.50, "f1": -1.0, "precision": 0.0, "recall": 0.0}
    for threshold in candidates:
        predictions = (probabilities >= threshold).astype(int)
        precision = precision_score(y_true, predictions, zero_division=0)
        recall = recall_score(y_true, predictions, zero_division=0)
        f1 = f1_score(y_true, predictions, zero_division=0)
        candidate = {"threshold": float(round(threshold, 2)), "f1": float(f1), "precision": float(precision), "recall": float(recall)}
        if f1 > best_overall["f1"]:
            best_overall = candidate
        if recall >= 0.60 and f1 > best_with_recall["f1"]:
            best_with_recall = candidate
    return best_with_recall if best_with_recall["f1"] >= 0 else best_overall


class Timer:
    def __enter__(self):
        self.started = perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_seconds = perf_counter() - self.started


def _safe_metric(metric, *args, **kwargs) -> float:
    try:
        return float(metric(*args, **kwargs))
    except ValueError:
        return 0.0
