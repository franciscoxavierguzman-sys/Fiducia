# Academic Final Architecture - FIDUCIA

Fecha: 2026-09-30  
Estado: Final academic configuration / E5 reference  
Uso: documentacion academica para capturas, defensa y trazabilidad del Proyecto Final de Grado PBS.

## 1. Alcance

Este documento registra la configuracion academica final de la investigacion. No reemplaza ni elimina los componentes historicos del prototipo, como `fraud-model-v1`, `risk-engine-v1.1`, la documentacion E4 ni los artefactos anteriores.

FIDUCIA debe presentarse como un prototipo tecnologico y experimental. No es una institucion financiera, no procesa remesas reales, no determina legalmente fraude y no valida desempeno sobre remesas reales de Guatemala.

## 2. Dataset Final

Dataset: PaySim  
Tipo: dataset sintetico de transacciones de dinero movil.  
Total: 6,362,620 transacciones.  
Fraudes: 8,213.  
Tasa de fraude aproximada: 0.1291 %.

Disclaimer:

Resultados experimentales obtenidos sobre el dataset sintetico PaySim. No representan desempeno validado sobre remesas reales de Guatemala.

## 3. Split Temporal

| Split | Steps | Registros | Fraudes | Uso |
|---|---:|---:|---:|---|
| TRAIN | 1-323 | 4,463,587 | 3,643 | Entrenamiento |
| VALIDATION | 324-377 | 943,289 | 560 | Seleccion de threshold y configuracion |
| TEST | 378-743 | 955,744 | 4,010 | Evaluacion final E5 |

TEST permanecio bloqueado durante el desarrollo y fue utilizado unicamente para la evaluacion final E5. No debe usarse para optimizar threshold, seleccionar variables ni ajustar hiperparametros.

## 4. Variables PaySim

Variables originales:

- `step`
- `type`
- `amount`
- `nameOrig`
- `oldbalanceOrg`
- `newbalanceOrig`
- `nameDest`
- `oldbalanceDest`
- `newbalanceDest`
- `isFraud`
- `isFlaggedFraud`

## 5. Variables Excluidas Por Leakage

Variables excluidas como predictores:

- `newbalanceOrig`
- `newbalanceDest`
- `isFlaggedFraud`
- `nameOrig`
- `nameDest`

`newbalanceOrig`, `newbalanceDest` e `isFlaggedFraud` se excluyen por riesgo de leakage o informacion posterior/no disponible de forma adecuada para inferencia honesta.

`nameOrig` y `nameDest` se excluyen como identificadores directos. Pueden utilizarse unicamente para derivar caracteristicas historicas construidas con informacion anterior a la transaccion evaluada, por ejemplo conteos o estadisticas acumuladas previas por entidad.

## 6. Evolucion Experimental

| Experimento | Descripcion |
|---|---|
| E0 | Dummy classifier |
| E1 | Logistic Regression balanceada |
| E2 | HistGradientBoosting balanceado |
| E3 | HistGradientBoosting + variables historicas construidas sin leakage |
| E4 | Evaluacion del Risk Engine hibrido original |
| E4.1 | Analisis de sensibilidad de pesos y seleccion de arquitectura |
| E5 | Evaluacion final sobre TEST con LightGBM |

La arquitectura final es resultado de experimentacion y no una seleccion arbitraria.

## 7. Modelo Experimental Final

Modelo experimental final: LightGBM.

Configuracion conceptual final:

- Machine Learning: componente predictivo principal.
- Rules: senales explicables complementarias.
- Anomaly Detection: senal complementaria.
- Risk Engine: capa de consolidacion, explicacion y apoyo a revision humana.
- Human Review: decision o revision humana.

`risk-engine-v1.1` con Rules 30 %, ML 50 % y Anomaly 20 % pertenece a la arquitectura historica/evaluada en E4. Debe conservarse como evidencia historica y experimental, pero no debe presentarse como arquitectura predictiva final optima.

## 8. Threshold Final

Threshold final:

```text
0.9946945188209642
```

Fue seleccionado utilizando VALIDATION y congelado antes de la evaluacion sobre TEST.

No debe recalcularse, optimizarse con TEST ni editarse desde la interfaz academica.

## 9. Resultados Finales E5

Evaluacion final E5 sobre holdout temporal TEST:

| Metrica | Valor |
|---|---:|
| TEST rows | 955,744 |
| Fraudes | 4,010 |
| No fraudes | 951,734 |
| PR-AUC | 0.8817398533 |
| ROC-AUC | 0.9985372055 |
| Precision | 0.9674796748 |
| Recall | 0.6825436409 |
| F1 | 0.8004094166 |
| Predicted positive | 2,829 |

## 10. Matriz de Confusion E5

|  | Predicho positivo | Predicho negativo |
|---|---:|---:|
| Positivo real | TP = 2,737 | FN = 1,273 |
| Negativo real | FP = 92 | TN = 951,642 |

Los 1,273 falsos negativos muestran que el modelo no debe interpretarse como mecanismo autonomo para confirmar o descartar fraude.

## 11. Arquitectura Final

La narrativa academica recomendada es:

Problema -> transaccion -> analisis de riesgo -> explicacion -> revision humana -> evaluacion experimental -> resultados E5 -> limitaciones.

FIDUCIA implementa el prototipo y permite visualizar esta narrativa, pero la investigacion no debe confundirse con un producto financiero real.

## 12. Limitaciones

- PaySim es sintetico.
- PaySim no representa transacciones reales de remesas de Guatemala.
- Los resultados E5 no son desempeno validado sobre remesas reales guatemaltecas.
- Un resultado HIGH no significa fraude confirmado.
- Un resultado LOW no garantiza legitimidad de la transaccion.
- El modelo no reemplaza revision humana.
- El prototipo no ejecuta controles regulatorios reales de AML, KYC o sanciones.
- La arquitectura historica E4 debe conservarse solo como evidencia de evolucion experimental.

## 13. Elementos Historicos Preservados

No deben eliminarse:

- `fraud-model-v1`
- `risk-engine-v1.1`
- documentacion E4
- resultados historicos
- artefactos anteriores
- arquitectura historica 30/50/20

Estos elementos demuestran evolucion experimental y deben etiquetarse como `HISTORICAL`, `PREVIOUS EXPERIMENT` o `E4 BASELINE` cuando se presenten junto a la configuracion final.

