# Forecast Model Card

## Name

FIDUCIA Remittance Forecast

## Version

`remittance-forecast-v1`

## Purpose

Estimar volumen y monto agregado de remesas para planificacion operativa dentro del prototipo.

## Dataset

Datos sinteticos procesados de FIDUCIA, agregados semanalmente.

## Targets

- `transaction_count`.
- `transaction_amount_usd`.

## Granularity And Horizon

- Granularidad: semanal.
- Horizonte permitido: 4, 8, 12 semanas.

## Selected Model

`Moving Average 8` para ambos targets.

## Metrics

Test:

- transaction_count: MAE 13.8854, RMSE 19.6157, WAPE 0.1098.
- transaction_amount_usd: MAE 4022.9019, RMSE 4961.8058, WAPE 0.1627.

## Prediction Intervals

Intervalos 80% y 95% basados en cuantiles absolutos de residuales validation.

## Intended Use

Analitica predictiva agregada para estimar carga operativa y actividad futura del prototipo.

## Out Of Scope

No predice remesas reales de Guatemala. No modifica scoring de riesgo, decisiones financieras, precios ni cumplimiento.

## Limitations

- Datos sinteticos.
- Solo 18 meses historicos.
- Eventos externos no incluidos.
- Incertidumbre crece con el horizonte.
- No garantiza resultados futuros.
