# Catalogo De KPIs BI

FIDUCIA Fase 7 centraliza las definiciones en `backend/app/bi/kpis.py`.

| Codigo | Nombre | Categoria | Formula | Unidad | Fuente |
| --- | --- | --- | --- | --- | --- |
| total_remittances | Remesas | NEGOCIO | `count(transactions)` | count | transactions |
| total_amount_usd_equivalent | Monto movilizado | NEGOCIO | `sum(source_amount * rate_to_usd[source_currency])` | USD equivalente | transactions + tasas configurables |
| average_ticket_usd_equivalent | Ticket promedio | TRANSACCIONES | `total_amount_usd_equivalent / total_remittances` | USD equivalente | transactions |
| total_commission_revenue_usd_equivalent | Ingresos por comision | INGRESOS | `sum(commission_amount * rate_to_usd[source_currency])` | USD equivalente | transactions.commission_amount |
| average_commission_usd_equivalent | Comision promedio | INGRESOS | `commission_revenue / total_remittances` | USD equivalente | transactions |
| active_clients | Clientes activos | CLIENTES | `count_distinct(sender_id)` | count | transactions.sender_id |
| active_corridors | Corredores activos | CORREDORES | `count_distinct(origin_country, destination_country)` | count | transactions |
| completion_rate | Tasa de finalizacion | OPERACIONES | `completed_remittances / eligible_remittances` | ratio | transactions.status |

## Definiciones

- `active_client`: remitente con al menos una remesa dentro del periodo filtrado.
- `new_client`: remitente cuya primera remesa historica cae dentro del periodo.
- `returning_client`: remitente con actividad antes del periodo y actividad dentro del periodo.
- `repeat_sender`: cliente activo con mas de una remesa dentro del periodo.
- `eligible_remittance`: remesa con estado operacional conocido: `AVAILABLE`, `COMPLETED`, `PROCESSING`, `REVIEW_REQUIRED`, `REJECTED`.

## Filtros

Todos los KPIs soportan `date_from`, `date_to`, `origin_country`, `destination_country`, `currency` y `status`.

## Limitaciones

Los KPIs monetarios globales usan USD equivalente con tasas configurables/sinteticas. No se exponen nombres, correos, telefonos ni rankings individuales de clientes.
