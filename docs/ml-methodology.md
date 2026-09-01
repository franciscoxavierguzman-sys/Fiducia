# Metodologia ML - FIDUCIA Fase 4

## Dataset

Se utilizo `data/processed/remittances_analytics.csv`, generado en Fase 3 con 10,000 remesas sinteticas.

Distribucion de clases:

- `fraud_label=0`: 9,632 registros.
- `fraud_label=1`: 368 registros.
- Tasa positiva: 3.68 %.

## Auditoria de leakage

Se excluyeron variables que revelan directamente la etiqueta, derivan de puntajes sinteticos o representan informacion posterior al evento:

- `fraud_label`
- `rule_score`
- `ml_probability`
- `anomaly_score`
- `final_risk_score`
- `risk_band_experimental`
- `status`
- `completed_at`
- `remittance_id`
- `remittance_number`
- `user_id`
- `beneficiary_id`
- `registration_date`
- `created_at`
- `historical_amount`
- `new_beneficiary`
- `weekend_transaction`
- `is_cross_border`

Las features finales estan en `ml/config.py`.

## Particion

Se aplico split estratificado:

- Train: 70 %.
- Validation: 15 %.
- Test: 15 %.

El conjunto test se mantuvo aislado para evaluacion final. La particion temporal se deja como mejora futura porque el dataset sintetico actual ya contiene features historicas precalculadas por evento, pero no simula drift operacional completo.

## Preprocessing

Se implemento `Pipeline` + `ColumnTransformer`:

- Numericas: imputacion con mediana; scaling para Logistic Regression.
- Categoricas: imputacion con moda y One-Hot Encoding.

El pipeline se guarda junto al modelo para que inferencia use exactamente las mismas transformaciones.

## Modelos

- DummyClassifier como baseline.
- Logistic Regression con `class_weight="balanced"`.
- Random Forest con profundidad y hojas controladas.
- HistGradientBoostingClassifier como Gradient Boosting.

## Threshold

Se evaluaron thresholds entre 0.10 y 0.90 en validation. Cada modelo guarda su threshold seleccionado. La probabilidad `ml_probability` se mantiene separada de la clasificacion visual.

## Calibracion

Se calcula Brier score como indicador simple de calibracion. No se aplico `CalibratedClassifierCV` en esta version para mantener el pipeline ligero y reproducible. Queda como mejora futura si se requiere calibracion formal.

## Explicabilidad

Para el modelo seleccionado se calculo permutation importance sobre validation con scoring `average_precision`.

Principales variables:

- `failed_transactions`
- `amount_vs_user_average`
- `max_transaction_amount`
- `failed_transaction_ratio`
- `commission_amount`
- `source_amount`
- `avg_transaction_amount`
- `transaction_count`

Estas variables no deben interpretarse como causas de fraude; son senales estadisticas en datos sinteticos.

