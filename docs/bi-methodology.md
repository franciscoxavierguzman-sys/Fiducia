# Metodologia BI

La capa BI es read-only y calcula agregaciones sobre datos operacionales existentes. No crea modelos nuevos, no recalcula riesgo y no reentrena forecasting.

## Multimoneda

Los montos globales se convierten a USD equivalente antes de agregarse:

`amount_usd = source_amount * EXCHANGE_RATES_TO_USD[source_currency]`

Las comisiones usan `commission_amount` historico almacenado y luego se convierten:

`commission_revenue_usd = commission_amount * EXCHANGE_RATES_TO_USD[source_currency]`

Esto preserva trazabilidad si la tasa de comision cambia en el futuro.

## Comparacion Temporal

Cuando el usuario envia `date_from` y `date_to`, BI calcula un periodo anterior equivalente. El crecimiento se calcula como:

`growth = (current - previous) / previous`

Si `previous = 0`, el crecimiento porcentual se reporta como `null`.

## Riesgo

BI lee `risk_assessments` historicos. No recalcula `rule_score`, `ml_probability`, `anomaly_score` ni `final_risk_score`.

## Forecasting

BI consume el resumen de `remittance-forecast-v1`. No modifica artefactos ni genera un modelo nuevo. El estado se presenta como experimental/conditional.

## Redondeo Y Tiempo

- Moneda: 2 decimales.
- Ratios: 4 decimales en API.
- Agregaciones temporales: basadas en `created_at` operacional.
