# Metodologia Risk Engine

`risk-engine-v1.1` combina tres senales independientes:

- `rule_score`: reglas deterministicas 0-100.
- `ml_probability`: probabilidad de `fraud-model-v1`, conservada 0-1.
- `anomaly_score`: comportamiento atipico 0-100 de `anomaly-model-v1`.

## Formula operativa

```text
ml_score = ml_probability * 100
final_risk_score = rules * 0.30 + ml_score * 0.50 + anomaly * 0.20
```

Si una senal no esta disponible, se excluye y los pesos restantes se renormalizan. No se usa cero para representar errores.

## Pesos

Los pesos favorecen ML porque es la senal supervisada validada en Fase 4, mantienen reglas con peso alto por explicabilidad y usan anomalias como complemento.

Estado metodologico: `Rules 30% / ML 50% / Anomaly 20%` se conserva como baseline heuristico inicial. No debe describirse como combinacion optima ni como configuracion estadisticamente optimizada.

## Bandas

- LOW: score < 25.
- MEDIUM: 25 <= score < 40.
- HIGH: score >= 40.

Estas bandas son thresholds operativos de Decision Support para el prototipo. No son thresholds regulatorios ni limites universales de fraude. `HIGH >= 40` busca aumentar sensibilidad del proceso de revision y reducir falsos negativos manteniendo un volumen razonable de revision manual.

## Acciones

- LOW -> CONTINUE.
- MEDIUM -> REVIEW.
- HIGH -> MANUAL_REVIEW.

El motor no bloquea, rechaza ni confirma fraude automaticamente.
