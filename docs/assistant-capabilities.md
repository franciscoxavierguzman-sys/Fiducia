# Assistant Capabilities

## Familias

- `SUPPORT`: ayuda general curada.
- `REMITTANCE`: remesas propias o remesas autorizadas.
- `BUSINESS_INTELLIGENCE`: KPIs y corredores desde BI.
- `FORECAST`: resumen de `remittance-forecast-v1`.
- `RISK_EXPLANATION`: snapshots existentes de `risk_assessments`.
- `BLOCKCHAIN_VERIFICATION`: historial y verificacion de evidencia.

## Intents

`GENERAL_HELP`, `MY_REMITTANCES`, `REMITTANCE_STATUS`, `REMITTANCE_FEES`, `BI_OVERVIEW`, `BI_CORRIDORS`, `BI_CUSTOMERS`, `FORECAST_SUMMARY`, `RISK_QUEUE`, `RISK_EXPLANATION`, `BLOCKCHAIN_TRACE`, `BLOCKCHAIN_VERIFY`, `OUT_OF_SCOPE`.

## Tools

- `get_support_article`: CLIENT, RISK_ANALYST, ADMIN.
- `get_my_remittances`: CLIENT, RISK_ANALYST, ADMIN.
- `get_remittance_status`: CLIENT, RISK_ANALYST, ADMIN.
- `get_remittance_fee`: CLIENT, RISK_ANALYST, ADMIN.
- `get_bi_overview`: RISK_ANALYST, ADMIN.
- `get_top_corridors`: RISK_ANALYST, ADMIN.
- `get_bi_customers`: RISK_ANALYST, ADMIN.
- `get_forecast_summary`: RISK_ANALYST, ADMIN.
- `get_risk_queue`: RISK_ANALYST, ADMIN.
- `get_risk_assessment`: RISK_ANALYST, ADMIN.
- `get_blockchain_trace`: CLIENT, RISK_ANALYST, ADMIN.
- `verify_blockchain_evidence`: CLIENT, RISK_ANALYST, ADMIN.
