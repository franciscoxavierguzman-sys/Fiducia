# Fase 5 - Plan del Risk Engine

## Objetivo

Construir `risk-engine-v1.1` encima de las Fases 1-4 sin reconstruir el proyecto, sin reentrenar `fraud-model-v1` y manteniendo el threshold operativo ML en `0.25`.

El motor combina tres senales auditables:

- Rule-based risk: reglas deterministicas y explicables.
- Machine learning risk: `ml_probability` de `fraud-model-v1`.
- Anomaly risk: `anomaly_score` no supervisado de `anomaly-model-v1`.

El resultado es un sistema de apoyo a decision, no un motor autonomo. Una evaluacion alta puede recomendar revision, pero no bloquea ni rechaza automaticamente una remesa.

## Arquitectura

```text
Transaction
  -> backend/app/risk/rules.py
  -> backend/app/services/ml_risk.py
  -> backend/app/risk/anomaly.py
  -> backend/app/risk/aggregator.py
  -> backend/app/services/risk_engine.py
  -> risk_assessments
  -> /api/v1/risk/*
  -> Frontend: Inteligencia de riesgo / Revision de riesgo
```

## Senales

### Reglas

Se implementan reglas calculables con datos operacionales existentes:

- R001: monto alto respecto a promedio historico del remitente.
- R002: velocidad transaccional de 24 horas.
- R003: velocidad transaccional de 7 dias.
- R004: beneficiario nuevo.
- R005: corredor nuevo para el usuario.
- R006: horario atipico.
- R007: incremento abrupto contra maximo historico.
- R008: diversidad de destinos en 30 dias.
- R009: ratio de transacciones fallidas recientes.
- R010: combinacion de senales conductuales.

No se usa pais o nacionalidad como proxy directo de fraude. El corredor solo cuenta si es nuevo para el comportamiento historico del usuario.

### Machine Learning

Se reutiliza `fraud-model-v1` sin reentrenamiento. La probabilidad se conserva como `ml_probability` entre 0 y 1. Para agregacion se usa `ml_score = ml_probability * 100`.

### Anomalias

Se usa Isolation Forest por compatibilidad con scikit-learn, costo razonable y naturaleza no supervisada. `fraud_label` no participa en entrenamiento. La salida nativa se transforma a `anomaly_score` 0-100 mediante percentiles calibrados sobre train.

## Normalizacion

- `rule_score`: ya se expresa 0-100 mediante suma acotada.
- `ml_score`: `ml_probability * 100`.
- `anomaly_score`: transformacion monotona reproducible de decision scores de Isolation Forest.

Si una senal falla, se marca como `unavailable`; no se sustituye con cero.

## Agregacion

Se evaluan combinaciones simples sobre validation:

- ML only
- Rules only
- Anomaly only
- ML + Rules
- ML + Anomaly
- Rules + Anomaly
- ML + Rules + Anomaly

Los pesos actuales se mantienen como baseline heuristico inicial. El test se reserva para cuantificacion final y no para optimizaciones posteriores.

## Bandas y acciones

Las bandas operativas autorizadas son:

- LOW: continuar flujo normal.
- MEDIUM: revision interna.
- HIGH: revision manual prioritaria.

Thresholds:

- LOW: `score < 25`.
- MEDIUM: `25 <= score < 40`.
- HIGH: `score >= 40`.

Estos thresholds son operativos de Decision Support, no regulatorios.

Las acciones quedan separadas:

- CONTINUE
- REVIEW
- MANUAL_REVIEW

Ninguna accion ejecuta rechazo financiero automatico.

## Persistencia y auditoria

Se agrega `risk_assessments` con snapshot completo de:

- scores por senal;
- versiones;
- reglas activadas;
- pesos;
- banda;
- accion recomendada;
- estado y decision humana.

Los eventos auditables esperados son:

- RISK_ASSESSMENT_CREATED
- RISK_ASSESSMENT_REEVALUATED
- RISK_REVIEW_COMPLETED
- RISK_REVIEW_ESCALATED

## Seguridad

Los endpoints internos son exclusivos para `ADMIN` y `RISK_ANALYST`. `CLIENT` conserva su flujo normal y no accede a cola ni detalles internos de riesgo.

## Limitaciones

Los resultados se basan en datos sinteticos. El motor no realiza AML real, KYC real, screening de sanciones ni decisiones regulatorias. Su objetivo es demostrar arquitectura, explicabilidad, trazabilidad y human-in-the-loop.
