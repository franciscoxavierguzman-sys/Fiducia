# Model Card - FIDUCIA Fraud Probability Model

## Model Name

FIDUCIA Fraud Probability Model

## Version

`fraud-model-v1`

## Purpose

Estimar una probabilidad de riesgo (`ml_probability`) para apoyar analisis interno de remesas.

## Algorithm

HistGradientBoostingClassifier.

## Training Dataset

`data/processed/remittances_analytics.csv`

- Registros: 10,000.
- Target positivo: 368.
- Dataset hash: `18c3b07edae88d373e0e50169015267a975c50a3315f7f919f6505f4147f2a27`.

## Target

`fraud_label`, etiqueta sintetica de potencial fraude.

## Features

37 features finales, documentadas en `ml/config.py` y `docs/phase4-ml-plan.md`.

## Excluded Features

Se excluyeron identificadores, target, scores sinteticos, estados posteriores y fechas directas con riesgo de leakage.

## Split Strategy

Split estratificado 70/15/15:

- Train: 7,000.
- Validation: 1,500.
- Test: 1,500.

## Metrics

Modelo seleccionado en test:

- Precision: 0.6286.
- Recall: 0.4000.
- F1: 0.4889.
- ROC-AUC: 0.8116.
- PR-AUC: 0.4728.
- Brier score: 0.0249.

## Threshold

`0.25`.

Clasificacion visual:

- Bajo: probabilidad menor que la mitad del threshold.
- Medio: probabilidad entre mitad del threshold y threshold.
- Alto: probabilidad mayor o igual al threshold.

## Intended Use

Apoyo al analisis de riesgo en entorno de investigacion y desarrollo del prototipo.

## Out-of-Scope Use

- Confirmar fraude real.
- Bloquear remesas automaticamente.
- Cumplimiento AML/KYC real.
- Decisiones regulatorias o financieras irreversibles.

## Synthetic Data Disclosure

El modelo fue entrenado con datos sinteticos. Sus resultados no deben interpretarse como desempeno demostrado sobre fraude financiero real.

## Ethical Considerations

El uso de pais, corredor, monto o metodo de pago puede inducir sesgos si se interpreta sin contexto. Ninguna variable debe utilizarse como justificacion automatica de fraude.

## Retraining Considerations

Reentrenar cuando cambie el generador, entren datos reales autorizados, se incorporen fuentes externas documentadas o se modifiquen features.
