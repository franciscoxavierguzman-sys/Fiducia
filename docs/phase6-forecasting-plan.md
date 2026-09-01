# Fase 6 - Plan de Forecasting

## Pregunta metodologica

¿El dataset actual permite forecasting metodologicamente defendible?

Respuesta: `CONDITIONAL`.

El dataset `data/processed/remittances_analytics.csv` cubre 18 meses, 540 dias y 78 semanas continuas. Es suficiente para un pronostico semanal experimental de corto plazo dentro del prototipo, pero no para afirmar predicciones reales del mercado de remesas.

## Alcance

- Forecast global semanal.
- Target principal: `transaction_count`.
- Target secundario: `transaction_amount_usd`.
- Horizonte: 4, 8 y 12 semanas.
- Top corredores: distribucion proporcional sobre corredores historicos principales.

## Separacion de Riesgo

Forecasting no modifica:

- `ml_probability`
- `anomaly_score`
- `rule_score`
- `final_risk_score`
- `risk_band`
- `recommended_action`

`fraud-model-v1`, `anomaly-model-v1`, `rules-v1` y `risk-engine-v1.1` permanecen intactos.

## Metodologia

Se usa split cronologico:

- Train: primer 70%.
- Validation: siguiente 15%.
- Test: ultimo 15%.

El modelo se selecciona por validation. Test solo cuantifica desempeno final.

## Decision De Granularidad

Se selecciona `weekly` porque reduce ruido diario y conserva 78 observaciones, suficientes para baselines y walk-forward validation de corto plazo.

## Modelos

- Naive.
- Seasonal Naive.
- Moving Average 4.
- Moving Average 8.
- HistGradientBoostingRegressor como candidato ML simple.

## Decision GO

`CONDITIONAL`: se permite Fase 6 con lenguaje experimental, datos sinteticos, horizonte corto e intervalos basados en residuales de validation.
