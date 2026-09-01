# FIDUCIA Fase 7 - Business Intelligence

## Objetivos

Construir una capa read-only de inteligencia de negocio que convierta transacciones, evaluaciones de riesgo y forecasting existente en KPIs ejecutivos, comparaciones temporales, rankings de corredores, analitica agregada de clientes, operaciones, riesgo y perspectiva predictiva.

## Usuarios

- ADMIN: acceso completo a Business Intelligence.
- RISK_ANALYST: acceso a overview, operaciones, riesgo, corredores y forecasting ejecutivo.
- CLIENT: sin acceso a BI interno.

## Fuentes De Datos

- `transactions`: remesas, montos, comisiones, monedas, estados, fechas, corredores.
- `users`: clientes agregados sin exponer PII.
- `risk_assessments`: snapshots historicos de riesgo y revision humana.
- `remittance-forecast-v1`: artefactos y servicio de forecasting ya existente.

## KPIs Y Formulas

Las formulas viven en `backend/app/bi/kpis.py` y se calculan desde `backend/app/bi/calculations.py`.

- `total_remittances`: conteo de remesas dentro de filtros.
- `total_amount_usd_equivalent`: suma de `source_amount * EXCHANGE_RATES_TO_USD[source_currency]`.
- `average_ticket_usd_equivalent`: monto USD equivalente / remesas.
- `total_commission_revenue_usd_equivalent`: suma de `commission_amount * EXCHANGE_RATES_TO_USD[source_currency]`.
- `average_commission_usd_equivalent`: revenue / remesas.
- `active_clients`: remitentes con al menos una remesa en el periodo.
- `active_corridors`: pares origen-destino con actividad.
- `completion_rate`: remesas `COMPLETED` / remesas elegibles.
- `new_clients`: clientes cuya primera remesa historica cae dentro del periodo.
- `returning_clients`: clientes con actividad previa al periodo y actividad en el periodo.
- `repeat_sender_rate`: clientes activos con mas de una remesa en el periodo / clientes activos.
- `growth_rate`: `(actual - anterior) / anterior`; si anterior es 0 se reporta `null`.

## Arquitectura

```
transactions / users / risk_assessments / forecast artifacts
        |
        v
backend/app/bi filtros + catalogo + calculos + comparaciones + insights
        |
        v
backend/app/services/business_intelligence.py
        |
        v
/api/v1/bi/*
        |
        v
Frontend - Inteligencia de negocio
```

## Permisos

Los endpoints BI requieren usuario autenticado con rol `ADMIN` o `RISK_ANALYST`. `CLIENT` recibe 403.

## Endpoints

- `GET /api/v1/bi/kpis`
- `GET /api/v1/bi/overview`
- `GET /api/v1/bi/trends`
- `GET /api/v1/bi/corridors`
- `GET /api/v1/bi/customers`
- `GET /api/v1/bi/operations`
- `GET /api/v1/bi/risk`
- `GET /api/v1/bi/forecast`
- `GET /api/v1/bi/executive-summary`
- `GET /api/v1/bi/exports/kpis.csv`
- `GET /api/v1/bi/exports/corridors.csv`

## Frontend

Crear seccion `Inteligencia de negocio` con filtros por fecha, pais, moneda y estado. Debe incluir KPIs ejecutivos, tendencia principal, ingresos por comision, ranking de corredores, clientes agregados, operaciones, riesgo agregado, forecast resumido e insights deterministricos.

## Riesgos Metodologicos

- Datos sinteticos: no representan comportamiento financiero real.
- FX configurable/sintetico: no debe presentarse como tasa historica oficial.
- Forecasting sigue en estado `CONDITIONAL`.
- No hacer inferencia causal.
- No exponer PII ni rankings individuales de clientes.

## Criterios De Aceptacion

- Branch `phase7-business-intelligence`.
- Fases 1-6 sin regresion.
- Catalogo central de KPIs.
- Formulas documentadas.
- API protegida.
- Dashboard ejecutivo funcional.
- Export CSV agregado y sin PII.
- Tests de formulas, filtros, autorizacion, riesgo, forecasting e insights.
- `npm run build` exitoso.
- Modelos Fases 4-6 intactos.
