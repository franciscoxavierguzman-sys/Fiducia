# Base de datos de FIDUCIA

FIDUCIA usa SQLite en el prototipo local mediante SQLAlchemy. La logica de negocio no depende directamente de SQLite, lo que permite migrar posteriormente a PostgreSQL.

## Tablas de Fase 1

- `roles`
- `users`

## Tablas agregadas en Fase 2

### `beneficiaries`

Beneficiarios ficticios asociados al usuario remitente.

Campos principales:

- `id`
- `sender_id`
- `beneficiary_user_id`
- `first_name`
- `last_name`
- `email`
- `phone`
- `relationship`
- `relationship_id`
- `relationship_other`
- `country`
- `currency`
- `city`
- `department`
- `municipality`
- `delivery_method`
- `bank_name`
- `account_type`
- `account_last_four`
- `is_active`
- `created_at`
- `updated_at`

`beneficiary_user_id` es opcional. Permite vincular un beneficiario con una cuenta FIDUCIA existente cuando el correo del beneficiario coincide con un usuario registrado.

### `countries`

Paises habilitados para origen y destino.

Seed inicial:

- Estados Unidos
- Canada
- Mexico
- Espana
- Guatemala

### `exchange_rates`

Tipos de cambio simulados y versionables por fecha.

Seed inicial:

```text
USD -> GTQ = 7.80
GTQ -> USD = 0.128205
CAD -> GTQ = 5.75
GTQ -> CAD = 0.173913
MXN -> GTQ = 0.46
GTQ -> MXN = 2.173913
EUR -> GTQ = 8.50
GTQ -> EUR = 0.117647
```

### `remittance_corridors`

Corredores origen-destino activos. Permiten activar o desactivar rutas sin duplicar logica en frontend/backend.

Campos principales:

- `origin_country_id`
- `destination_country_id`
- `origin_currency`
- `destination_currency`
- `is_active`
- `min_amount`
- `max_amount`
- `estimated_delivery`

### `transactions`

Remesas/transacciones del prototipo. Guardan una fotografia logica de los valores de calculo para que cambios futuros de configuracion no alteren historicos.

Campos financieros:

- `source_amount`
- `source_currency`
- `destination_currency`
- `funding_source_id`
- `remittance_uuid`
- `amount`
- `exchange_rate`
- `commission_rate`
- `commission_amount`
- `total_amount`
- `destination_amount`

Campos de ciclo transaccional:

- `sender_id`
- `beneficiary_id`
- `beneficiary_user_id`
- `status`
- `created_at`
- `updated_at`

`beneficiary_user_id` se copia desde el beneficiario al momento de crear la remesa. Si posteriormente se vincula el beneficiario con una cuenta, las transacciones asociadas pueden actualizar ese vinculo para habilitar la vista de remesas recibidas.

### `funding_sources`

Metodos de pago ficticios del usuario.

Campos principales:

- `user_id`
- `type`
- `display_name`
- `provider`
- `last_four`
- `currency`
- `is_default`
- `is_active`

### `beneficiary_relationships`

Catalogo de relaciones permitidas para beneficiarios.

### `departments` y `municipalities`

Catalogos de Guatemala para validar la relacion departamento -> municipio.

### `remittance_status_history`

Historial de cambios de estado de cada remesa.

Campos principales:

- `transaction_id`
- `previous_status`
- `new_status`
- `changed_at`
- `changed_by`
- `reason`

Campos preparados para fases posteriores:

- `rule_score`
- `ml_probability`
- `anomaly_score`
- `final_risk_score`
- `risk_level`
- `model_version`

### `audit_logs`

Registra eventos relevantes sin almacenar secretos ni tokens.

Eventos actuales:

- `BENEFICIARY_CREATED`
- `BENEFICIARY_UPDATED`
- `REMITTANCE_CREATED`
- `FUNDING_SOURCE_ADDED`
- `REMITTANCE_COMPLETED`

## Precision financiera

Los calculos se realizan con `Decimal`.

- Montos: `NUMERIC(12, 2)` o `NUMERIC(14, 2)`.
- Tipo de cambio: `NUMERIC(12, 6)`.
- Comision: `NUMERIC(8, 6)`.
- Redondeo: `ROUND_HALF_UP`.

## Capa analitica Fase 3

La Fase 3 no crea tablas nuevas en SQLite operacional. La separacion queda asi:

- Base operacional: usuarios, beneficiarios, metodos de pago, remesas, tracking y auditoria.
- Capa analitica de investigacion: archivos en `data/synthetic/`, `data/raw/`, `data/external/` y `data/processed/`.
- API analitica: endpoints `/api/v1/analytics/*` que leen agregados de la base operacional con autorizacion por rol.

Datasets generados:

- `data/synthetic/remittances_synthetic.csv`
- `data/processed/remittances_analytics.csv`
- `data/processed/validation_report.json`
- `data/processed/descriptive_summary.json`

El dataset analitico no contiene contrasenas, JWT, CVV, numeros completos de tarjetas, numeros completos de cuentas, PIN, credenciales ni secretos.

## Risk Assessments Fase 5

`risk_assessments` almacena el snapshot de cada evaluacion:

- `remittance_id`
- `assessment_sequence`
- `rule_score`, `rules_version`, `triggered_rules_json`
- `ml_probability`, `ml_model_version`, `ml_threshold`
- `anomaly_score`, `anomaly_model_version`
- `final_risk_score`, `risk_band`, `recommended_action`
- `risk_engine_version`, `weights_json`, `signal_status_json`, `explanations_json`
- `review_status`, `reviewed_by`, `review_decision`, `review_reason`, `reviewed_at`

Una reevaluacion crea una nueva secuencia para conservar trazabilidad historica.

## Forecasting Fase 6

Tablas:

- `forecast_runs`
- `forecast_values`

Permiten conservar snapshots de pronosticos generados:

- modelo y version;
- target;
- granularidad;
- horizonte;
- cutoff de entrenamiento;
- periodo pronosticado;
- valor estimado;
- intervalos 80/95;
- `actual_value` nullable para comparacion futura.
