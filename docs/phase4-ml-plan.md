# FIDUCIA Fase 4 - Plan de Machine Learning

## Objetivo

Construir una capa reproducible y explicable de Machine Learning supervisado para estimar `ml_probability`, la probabilidad de que una remesa corresponda a un patron de fraude segun variables disponibles en el dataset sintetico de Fase 3.

El modelo opera como apoyo al analisis de riesgo. No bloquea remesas, no confirma fraude real y no reemplaza KYC, AML ni controles regulatorios.

## Target

- Variable: `fraud_label`
- Valores: `0` no fraude sintetico, `1` fraude sintetico
- Naturaleza: etiqueta sintetica generada para investigacion y desarrollo del prototipo.

## Features candidatas incluidas

| Feature | Included / Excluded | Reason |
| --- | --- | --- |
| account_age_days | Included | Disponible antes de evaluar la remesa y captura madurez de cuenta. |
| transaction_count | Included | Historial previo disponible al momento de operacion. |
| source_amount | Included | Monto de remesa disponible antes de decision. |
| commission_rate | Included | Parametro de cotizacion disponible. |
| commission_amount | Included | Derivado del monto y tasa antes de confirmar. |
| total_debit_amount | Included | Costo total conocido antes de confirmar. |
| exchange_rate | Included | Tipo de cambio aplicado a la cotizacion. |
| destination_amount | Included | Monto destino calculado antes de confirmar. |
| linked_user | Included | Indicador operativo del beneficiario. |
| transactions_last_24h | Included | Feature historica previa. |
| transactions_last_7d | Included | Feature historica previa. |
| transactions_last_30d | Included | Feature historica previa. |
| avg_transaction_amount | Included | Promedio historico previo. |
| max_transaction_amount | Included | Maximo historico previo. |
| new_beneficiary_flag | Included | Basado en antiguedad del beneficiario. |
| beneficiary_age_days | Included | Disponible antes de evaluar. |
| countries_used_last_30d | Included | Diversidad historica previa. |
| failed_transactions | Included | Historial previo de fallas. |
| transaction_hour | Included | Hora de evento disponible al momento. |
| weekend_flag | Included | Derivado de fecha/hora del evento. |
| amount_vs_user_average | Included | Comparacion contra historial previo. |
| transaction_velocity_24h | Included | Alias operacional de velocidad. |
| transaction_velocity_7d | Included | Alias operacional de velocidad. |
| unusual_hour_flag | Included | Derivado de hora del evento. |
| new_corridor_flag | Included | Basado en historial previo del usuario. |
| country_diversity_30d | Included | Diversidad historica previa. |
| failed_transaction_ratio | Included | Ratio historico previo. |
| historical_avg_amount | Included | Historial previo. |
| historical_max_amount | Included | Historial previo. |
| origin_country | Included | Variable de corredor; se documenta riesgo de sesgo y no debe usarse como justificacion automatica. |
| destination_country | Included | Variable de corredor; se documenta riesgo de sesgo y no debe usarse como justificacion automatica. |
| source_currency | Included | Contexto transaccional. |
| destination_currency | Included | Contexto transaccional. |
| delivery_method | Included | Metodo elegido antes de evaluar. |
| funding_method | Included | Metodo elegido antes de evaluar. |
| relationship | Included | Relacion declarada del beneficiario. |
| amount_bucket | Included | Derivado de monto actual, no del target. |

## Features excluidas y leakage

| Feature | Included / Excluded | Reason |
| --- | --- | --- |
| fraud_label | Excluded | Target. |
| rule_score | Excluded | Fue construido usando senales relacionadas con la etiqueta sintetica. |
| ml_probability | Excluded | Placeholder de Fase 3; seria fuga directa y circular. |
| anomaly_score | Excluded | Puntaje sintetico derivado de senales de riesgo. |
| final_risk_score | Excluded | Mezcla sintetica posterior. |
| risk_band_experimental | Excluded | Derivado de `final_risk_score`. |
| status | Excluded | Estado posterior/consecuencia operativa. |
| completed_at | Excluded | Solo existe despues del evento. |
| remittance_id | Excluded | Identificador sin senal generalizable. |
| remittance_number | Excluded | Identificador sin senal generalizable. |
| user_id | Excluded | Riesgo de memorizar usuarios sinteticos. |
| beneficiary_id | Excluded | Riesgo de memorizar beneficiarios sinteticos. |
| registration_date | Excluded | Se usa `account_age_days` como representacion numerica. |
| created_at | Excluded | Se usan `transaction_hour` y flags temporales. |
| historical_amount | Excluded | Redundante frente a promedios, maximos y conteos. |
| new_beneficiary | Excluded | Duplicado de `new_beneficiary_flag`. |
| weekend_transaction | Excluded | Duplicado de `weekend_flag`. |
| is_cross_border | Excluded | Constante en el dataset actual. |

## Estrategia de particion

Se utiliza particion aleatoria estratificada 70 % train, 15 % validation y 15 % test con seed configurable. El dataset sintetico contiene estructura temporal, pero las features historicas fueron calculadas previamente por evento en Fase 3. Una particion temporal se documenta como recomendacion futura cuando el generador incorpore ventanas mas realistas por usuario y se quiera evaluar drift.

El conjunto test se mantiene aislado hasta la evaluacion final del modelo seleccionado.

## Desbalance de clases

El dataset tiene alrededor de 3.68 % de casos `fraud_label=1`. Accuracy no se usa como metrica principal. Se evaluan precision, recall, F1, ROC-AUC, PR-AUC, Brier score y matriz de confusion.

## Modelos candidatos

- DummyClassifier como baseline.
- Logistic Regression con `class_weight="balanced"`.
- Random Forest con parametros controlados.
- HistGradientBoostingClassifier como Gradient Boosting disponible en scikit-learn.

## Preprocessing

Se usa `Pipeline` y `ColumnTransformer`:

- Numericas: imputacion mediana y scaling cuando aplica.
- Categoricas: imputacion de moda y One-Hot Encoding.

El preprocessing se guarda junto al modelo seleccionado para inferencia.

## Threshold y calibracion

Se analizan thresholds entre 0.10 y 0.90 sobre validation. La seleccion favorece F1 y recall de fraude sin colapsar precision. El threshold operativo validado para `fraud-model-v1` es `0.25`. Se calcula Brier score como diagnostico simple de calibracion. No se aplica calibracion adicional en esta version para mantener el flujo reproducible y ligero; queda documentado como mejora.

## Explicabilidad

Se usan coeficientes para Logistic Regression e importancias para modelos de arboles cuando esten disponibles. Para explicabilidad local se reportan contribuciones aproximadas de features transformadas para modelos lineales y top importances globales como contexto.

## Criterios de seleccion

Se prioriza:

1. PR-AUC frente a baseline.
2. Recall de fraude no trivial.
3. Precision mayor a cero.
4. Interpretabilidad.
5. Reproducibilidad.
6. Facilidad de integracion en FastAPI.

## Limitaciones

- Entrenado con datos sinteticos, no con fraude financiero real confirmado.
- Las variables de pais/corredor pueden inducir sesgos si se interpretan mal.
- No debe automatizar rechazos ni bloqueos.
- No implementa Risk Engine definitivo ni anomaly detection productivo.
