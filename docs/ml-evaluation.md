# Evaluacion ML - FIDUCIA Fase 4

## Comparacion de modelos

| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | Threshold |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dummy | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.0367 | 0.50 |
| Logistic Regression | 0.1650 | 0.6182 | 0.2605 | 0.7930 | 0.4310 | 0.55 |
| Random Forest | 0.1911 | 0.5455 | 0.2830 | 0.8048 | 0.4175 | 0.40 |
| Gradient Boosting | 0.6286 | 0.4000 | 0.4889 | 0.8116 | 0.4728 | 0.25 |

## Modelo seleccionado

Se selecciono `Gradient Boosting` (`HistGradientBoostingClassifier`) como `fraud-model-v1`.

Razon:

- Mejor PR-AUC en test frente a baseline y modelos candidatos.
- Mejor F1 entre los modelos evaluados con threshold operativo validado.
- Precision razonable y mejor recall que el threshold 0.50.
- Recall no trivial, aunque inferior al de Logistic Regression.
- Entrenamiento rapido y reproducible.

## Trade-off

Logistic Regression detecta mas casos positivos (`recall=0.6182`) pero con baja precision (`0.1650`), lo que generaria muchos falsos positivos. Gradient Boosting con threshold `0.25` ofrece mejor F1 (`0.4889`) y una precision todavia razonable (`0.6286`), elevando el recall frente al threshold `0.50`.

## Matriz de confusion del modelo seleccionado

```text
TN: 1432 | FP: 13
FN:   33 | TP: 22
```

## Validacion de independencia validation/test

Se verifico que `X_validation` y `X_test` son objetos distintos, con subconjuntos distintos y sin solapamiento de indices. Las predicciones de validation y test se generaron en llamadas independientes a `predict_proba`.

- Registros train: 7,000.
- Registros validation: 1,500.
- Registros test: 1,500.
- Distribucion validation: `fraud_label=0`: 1,445; `fraud_label=1`: 55.
- Distribucion test: `fraud_label=0`: 1,445; `fraud_label=1`: 55.
- Hash indices validation: `301909b3fd86b937db57d5433d729102ca619d23702aad93ae40b7b2214282b5`.
- Hash indices test: `95e5f26170b24a2f106d6ad93af5611eedd55515ef8f937aae995b092dd6b557`.
- Fingerprint registros validation: `df08657419b3c5980ff7bba99fa7466aa53b9cfbd2e1a03250fc266b4e802ea5`.
- Fingerprint registros test: `9effc99f6923f75ff4164f80c3b91ccf9eeb9ce8851ac717bf7d237ede0d6b5f`.
- Solapamiento de indices: 0.

La coincidencia de matriz de confusion para threshold `0.25` en validation y test es una coincidencia del conteo, no reutilizacion de predicciones o datasets.

## Limitaciones

- Datos sinteticos, no fraude financiero real confirmado.
- La seleccion puede cambiar si se prioriza recall operativo sobre precision.
- No implementa decision automatica.
- No debe usarse como control AML/KYC real.
