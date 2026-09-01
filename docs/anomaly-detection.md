# Anomaly Detection

Modelo: `anomaly-model-v1`.

Algoritmo: Isolation Forest.

Entrenamiento:

```powershell
.\backend\.venv\Scripts\python.exe scripts\train_anomaly_model.py --seed 42
```

## Features

Incluye variables conductuales como monto, velocidad, antiguedad del beneficiario, ratio de fallas, horario, corredor nuevo y metodos. Excluye `fraud_label`, `ml_probability`, `rule_score` y `final_risk_score`.

## Normalizacion

La salida nativa de Isolation Forest no se presenta como probabilidad. Se transforma asi:

```text
score = clip((p99_train_decision - decision_score) / (p99 - p1) * 100, 0, 100)
```

0 significa comportamiento consistente con patrones normales; 100 indica comportamiento extremadamente atipico.

## Evaluacion

`fraud_label` solo se usa posteriormente para evaluar capacidad discriminativa experimental.

Resultados test:

- ROC-AUC contra etiqueta sintetica: 0.6529.
- PR-AUC contra etiqueta sintetica: 0.0812.
- Media normal: 40.74.
- Media fraud_label=1: 53.59.
