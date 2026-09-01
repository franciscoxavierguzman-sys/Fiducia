# Blockchain Evidence Schema

## remittance-evidence-v1

Campos permitidos:

- `schema_version`
- `event_type`
- `entity_type`
- `entity_reference`
- `remittance_number`
- `origin_country`
- `destination_country`
- `source_currency`
- `destination_currency`
- `source_amount`
- `commission_amount`
- `status`
- `occurred_at`

## risk-evidence-v1

Campos permitidos:

- `schema_version`
- `event_type`
- `entity_type`
- `entity_reference`
- `risk_assessment_id`
- `risk_engine_version`
- `rules_version`
- `ml_model_version`
- `anomaly_model_version`
- `final_risk_score`
- `risk_band`
- `evaluated_at`

## Campos Prohibidos

Nombre, apellido, email, telefono, direccion, DPI, pasaporte, cuenta bancaria, tarjeta, banco, JWT, passwords y tokens.
