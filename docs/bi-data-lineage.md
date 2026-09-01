# BI Data Lineage

## KPIs Ejecutivos

```
transactions
  -> backend/app/bi/calculations.py
  -> backend/app/services/business_intelligence.py
  -> /api/v1/bi/overview
  -> Frontend Inteligencia de negocio
```

## Corredores

```
transactions.origin_country + transactions.destination_country
  -> corridor aggregations
  -> /api/v1/bi/corridors
  -> ranking ejecutivo y CSV agregado
```

## Riesgo

```
risk_assessments
  -> agregacion por risk_band y review_status
  -> /api/v1/bi/risk
  -> dashboard BI
```

BI no reinterpreta assessments historicos con configuracion actual.

## Forecast

```
ml/artifacts/forecasting
reports/forecasting
  -> app.services.forecasting.get_forecast_summary()
  -> /api/v1/bi/forecast
  -> panel "Perspectiva proximas semanas"
```
