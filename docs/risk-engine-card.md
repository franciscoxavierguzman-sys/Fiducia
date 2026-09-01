# Risk Engine Card

## Name

FIDUCIA Risk Engine

## Version

`risk-engine-v1.1`

## Purpose

Apoyar a analistas internos con una evaluacion explicable de riesgo para remesas digitales.

## Components

- Rules: `rules-v1`.
- ML: `fraud-model-v1`, Gradient Boosting, threshold 0.25.
- Anomaly Detection: `anomaly-model-v1`, Isolation Forest.

## Inputs

Features operacionales de remesa, historial de usuario, beneficiario, corredor, monto, moneda, metodo de fondeo y metodo de entrega.

## Outputs

- `rule_score`
- `ml_probability`
- `anomaly_score`
- `final_risk_score`
- `risk_band`
- `recommended_action`
- explicaciones deterministicas

## Aggregation Method

Ponderacion de senales disponibles:

- Rules: 30%.
- ML: 50%.
- Anomaly: 20%.

Estos pesos son un baseline heuristico inicial, no una configuracion optima.

## Risk Bands

- LOW: < 25.
- MEDIUM: 25 a < 40.
- HIGH: >= 40.

Las bandas son thresholds operativos de Decision Support; no son limites regulatorios ni fraude confirmado.

## Recommended Actions

- LOW -> CONTINUE.
- MEDIUM -> REVIEW.
- HIGH -> MANUAL_REVIEW.

## Validation Methodology

Pesos mantenidos como baseline heuristico inicial. `HIGH >= 40` fue autorizado como ajuste operativo para aumentar sensibilidad de revision. TEST se reporta para cuantificacion final, no para optimizacion posterior.

## Performance

Test Full Risk Engine:

- Precision: 0.6452.
- Recall: 0.3636.
- F1: 0.4651.
- ROC-AUC: 0.8072.
- PR-AUC: 0.4217.

## Human Oversight

El analista registra `APPROVE`, `ESCALATE` o `REJECT`. Rechazo y escalamiento exigen justificacion.

## Known Limitations

Datos sinteticos, sin KYC real, sin AML real, sin sanciones, sin decisiones financieras automaticas.

## Intended Use

Demostracion academica/profesional de arquitectura de riesgo, trazabilidad y revision humana.

## Out-of-Scope Use

Bloqueo automatico, acusaciones de fraude, scoring regulatorio real o evaluaciones sobre clientes reales.

## Ethical Considerations

Evita atributos sensibles. Pais/corredor no se usa como proxy directo de fraude. Los falsos positivos generan revision adicional; los falsos negativos pueden omitir senales relevantes.
