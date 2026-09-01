# Evaluacion Risk Engine

Dataset: `data/processed/remittances_analytics.csv`.

Split reproducible:

- Train: 7000.
- Validation: 1500.
- Test: 1500.

TEST se reporta para cuantificar el efecto de la configuracion autorizada. No se usa para volver a optimizar thresholds.

## Resultados validation

Full Risk Engine:

- Precision: 0.7500.
- Recall: 0.3636.
- F1: 0.4651.
- ROC-AUC: 0.7878.
- PR-AUC: 0.4005.
- Confusion Matrix: `[[1434, 11], [35, 20]]`.

## Resultados test

Full Risk Engine:

- Precision: 0.7826.
- Recall: 0.3636.
- F1: 0.4651.
- ROC-AUC: 0.8072.
- PR-AUC: 0.4217.
- Confusion Matrix: `[[1434, 11], [35, 20]]`.
- TP: 20.
- TN: 1434.
- FP: 11.
- FN: 35.

## Comparacion HIGH >= 50 vs HIGH >= 40

Validation:

- HIGH >= 50: TP 12, TN 1441, FP 4, FN 43, Recall 0.2182, F1 0.3380.
- HIGH >= 40: TP 20, TN 1434, FP 11, FN 35, Recall 0.3636, F1 0.4651.

Test:

- HIGH >= 50: TP 18, TN 1440, FP 5, FN 37, Recall 0.3273, F1 0.4615.
- HIGH >= 40: TP 20, TN 1434, FP 11, FN 35, Recall 0.3636, F1 0.4651.

Distribucion de bandas con `HIGH >= 40`:

- Validation: LOW 1360, MEDIUM 109, HIGH 31.
- Test: LOW 1341, MEDIUM 128, HIGH 31.

## Ablation Study

El reporte completo esta en `reports/risk_engine/ablation_results.json`.

| Variante | Precision test | Recall test | F1 test | PR-AUC test |
| --- | ---: | ---: | ---: | ---: |
| ML only threshold 0.25 | 0.6286 | 0.4000 | 0.4889 | 0.4728 |
| Rules only | 0.2615 | 0.3091 | 0.2833 | 0.1670 |
| Anomaly only | 0.0601 | 0.5455 | 0.1083 | 0.0812 |
| ML + Rules | 0.8500 | 0.3091 | 0.4533 | 0.4465 |
| ML + Anomaly | 0.8000 | 0.2909 | 0.4267 | 0.4316 |
| Rules + Anomaly | 0.1628 | 0.3818 | 0.2283 | 0.1738 |
| Full Risk Engine | 0.6452 | 0.3636 | 0.4651 | 0.4217 |

ML only conserva mejor F1 y PR-AUC. La principal ventaja de `risk-engine-v1.1` es trazabilidad, explicabilidad operacional y human-in-the-loop, no superar necesariamente la capacidad predictiva del modelo supervisado.
