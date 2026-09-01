# Arquitectura de FIDUCIA

FIDUCIA inicia como un monorepo modular con frontend React, backend FastAPI, base de datos SQLite mediante SQLAlchemy y carpetas separadas para ML, datos y documentacion.

```text
frontend -> /api/v1 -> backend -> SQLAlchemy -> SQLite
                              |
                              +-> capa analitica Fase 3
                              +-> modulo ML Fase 4
```

La decision de mantener backend y ML en Python reduce friccion para el componente academico de inteligencia artificial. En Fase 1 el modulo ML queda preparado por estructura, pero no se entrena ningun modelo.

## Principios

- La logica de negocio no debe depender directamente de SQLite.
- La configuracion vive en variables de entorno.
- Los nombres tecnicos se mantienen en ingles.
- La interfaz visible se mantiene en espanol.
- Los datos sinteticos, externos y procesados permanecen separados.

## Extension Fase 2

La Fase 2 agrega el nucleo transaccional:

```text
Cliente autenticado
  -> Perfil
  -> Metodos de pago
  -> Beneficiarios
  -> Cotizacion
  -> Remesas enviadas
  -> Remesas recibidas
  -> Tracking
  -> Recepcion/cobro
```

Los calculos financieros se centralizan en `backend/app/services/remittances.py` y utilizan `Decimal`. El frontend consume la simulacion desde backend y no replica formulas financieras como fuente de verdad.

## Rebaseline del nucleo transaccional

La arquitectura consolidada mantiene FastAPI como fuente de verdad para autenticacion, perfil, catalogos, beneficiarios, vinculacion, metodos de pago ficticios, cotizacion, creacion de remesas, tracking, recepcion/cobro y auditoria.

El frontend solo orquesta flujos y presenta estados. No calcula comisiones ni modifica estados directamente.

Los nombres publicos de remesa se exponen como `remittance_number`, conservando `transaction_id` como columna compatible.

## Extension Fase 3

La Fase 3 separa la base operacional de la capa analitica:

```text
SQLite operacional
  -> endpoints /analytics de solo lectura

data/synthetic
  -> scripts/data_pipeline.py
  -> data/processed/remittances_analytics.csv
  -> validaciones y analitica descriptiva
```

Los endpoints de analitica consultan la operacion agregada y requieren rol `ADMIN` o `RISK_ANALYST`. El pipeline de investigacion no inserta datos sinteticos en SQLite operacional.

## Extension Fase 4

La Fase 4 agrega un pipeline ML separado:

```text
data/processed/remittances_analytics.csv
  -> ml/training/train.py
  -> ml/artifacts/fraud_model.joblib
  -> backend/app/services/ml_risk.py
  -> /api/v1/risk/ml/*
  -> frontend Inteligencia de riesgo
```

El backend puede iniciar aunque el modelo no exista; los endpoints reportan disponibilidad o error controlado. La inferencia usa el mismo preprocessing guardado en el artefacto interno.

## Extension Fase 5

La Fase 5 agrega `risk-engine-v1.1` como capa de decision support:

```text
Remesa
  -> Rule Engine rules-v1
  -> fraud-model-v1
  -> anomaly-model-v1
  -> Risk Aggregator
  -> risk_assessments
  -> Revision humana por ADMIN/RISK_ANALYST
```

El motor persiste snapshots de cada evaluacion para que cambios posteriores de reglas, pesos o modelos no alteren historicos. La remesa no se bloquea ni se rechaza automaticamente por score de riesgo.

## Extension Fase 6

La Fase 6 agrega forecasting como modulo analitico independiente:

```text
data/processed/remittances_analytics.csv
  -> data/processed/forecasting/weekly_remittances_forecasting.csv
  -> ml/artifacts/forecasting/*
  -> backend/app/services/forecasting.py
  -> /api/v1/forecasting/*
  -> frontend Analitica predictiva
```

Forecasting trabaja con datos agregados y no modifica ningun score o decision del Risk Engine.

## Extension Fase 7

La Fase 7 agrega Business Intelligence como capa read-only:

```text
transactions / users / risk_assessments / forecast artifacts
  -> backend/app/bi/*
  -> backend/app/services/business_intelligence.py
  -> /api/v1/bi/*
  -> frontend Inteligencia de negocio
```

BI no recalcula riesgo, no reentrena forecasting, no crea un modelo nuevo y no expone PII en el dashboard ejecutivo.
