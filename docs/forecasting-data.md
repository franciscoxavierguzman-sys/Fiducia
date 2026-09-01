# Datos De Forecasting

## Auditoria Temporal

- Registros: 10,000.
- Fecha inicial: 2025-03-06.
- Fecha final: 2026-08-27.
- Dias cubiertos: 540.
- Semanas cubiertas: 78.
- Meses cubiertos: 18.
- Huecos diarios: 0.
- Duplicados temporales exactos: 1.
- Continuidad semanal: continua.

Decision: `CONDITIONAL`.

## Dataset Semanal

Archivo: `data/processed/forecasting/weekly_remittances_forecasting.csv`.

Hash: `475cb49aae8ffc62de3195cc421c1ea0a054d5a3fb602fe28dc612cbfd941bf1`.

Columnas:

- `period`
- `transaction_count`
- `transaction_amount_usd`

## Multimoneda

Los montos se presentan como `USD equivalent`. No se suman USD, GTQ, MXN, EUR y CAD como si fueran la misma moneda.

## Limitaciones

Los datos son sinteticos y no reflejan comportamiento economico real de Guatemala ni de corredores internacionales.
