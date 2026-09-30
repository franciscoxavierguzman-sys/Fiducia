# Fiducia Final Academic Audit

Fecha: 2026-09-30  
Modo de ejecucion: auditoria estatica, comparacion y reporte.  
Restriccion aplicada: no se modifico codigo funcional, base de datos, modelos, configuraciones, frontend, backend, datasets, thresholds ni resultados.  
Archivo generado por solicitud: `FIDUCIA_FINAL_AUDIT.md`.

## 1. Executive Summary

FIDUCIA esta funcionalmente avanzado como prototipo, pero la version actual del repositorio no esta alineada con la arquitectura academica final descrita para el Proyecto Final de Grado PBS.

La aplicacion y la documentacion tecnica vigente siguen reflejando la arquitectura previa basada en `risk-engine-v1.1`, `fraud-model-v1`, `HistGradientBoostingClassifier`, threshold `0.25`, dataset sintetico interno de 10,000 remesas y agregacion `Rules 30% / ML 50% / Anomaly 20%`.

La investigacion final, en cambio, debe presentar:

- PaySim como dataset experimental final.
- Split temporal TRAIN / VALIDATION / TEST.
- LightGBM como componente predictivo principal.
- Threshold congelado `0.9946945188209642`.
- Resultados E5 sobre TEST.
- Rules y Anomaly como senales complementarias.
- Risk Engine como capa de consolidacion, explicabilidad y apoyo a revision humana.

La brecha principal no es que Fiducia sea inutilizable, sino que todavia muestra o conserva evidencia de fases tecnicas anteriores que no deben aparecer como arquitectura predictiva final ni como resultados academicos definitivos.

## 2. Academic Alignment

### Estado general

Clasificacion: IMPORTANT

FIDUCIA esta alineado como prototipo academico en terminos generales: el README, el footer del frontend y varios documentos indican que no es entidad financiera ni servicio real de remesas.

Evidencia:

- `README.md`: declara que FIDUCIA es prototipo tecnologico con fines educativos y de investigacion.
- `frontend/src/main.tsx`: footer visible con el mismo disclaimer general.
- `research/README.md` y `research/01_anteproyecto/*`: refuerzan que Fiducia es instrumento tecnologico, no investigacion en si misma.

### Brecha academica principal

Clasificacion: CRITICAL

La version actual no refleja todavia el titulo/pregunta/objetivo final como arquitectura experimental final dentro de una pantalla academica o modulo de resultados. La pantalla mas cercana es `Inteligencia de riesgo`, pero muestra metricas y modelo de la fase previa.

## 3. Current Architecture

### Arquitectura implementada actualmente

Clasificacion: CRITICAL

El backend activo conserva:

- `risk-engine-v1.1`.
- `RISK_ENGINE_WEIGHTS = {"rules": 0.30, "ml": 0.50, "anomaly": 0.20}` en `backend/app/risk/aggregator.py`.
- `risk_band_thresholds = {"medium": 25.0, "high": 40.0}`.
- `fraud-model-v1` como modelo ML.
- `HistGradientBoostingClassifier` como algoritmo.
- threshold ML activo `0.25`.

Esto contradice la arquitectura academica final, donde ML debe ser el componente predictivo principal y el Risk Engine debe presentarse como capa de consolidacion, no como modelo predictivo final optimo.

### Riesgo de presentacion

Clasificacion: CRITICAL

Si se toman capturas ahora, se documentara la arquitectura vieja como si fuera final.

## 4. Risk Engine Audit

### Hallazgo RE-01

Clasificacion: CRITICAL

`backend/app/risk/aggregator.py` calcula el score final con pesos `30/50/20`. Aunque el metadata dice "baseline heuristico inicial", el sistema sigue usando esos pesos de forma activa.

Impacto: contradice la decision academica final si se presenta como arquitectura seleccionada.

### Hallazgo RE-02

Clasificacion: IMPORTANT

`docs/risk-engine-methodology.md` y `docs/risk-engine-card.md` explican correctamente que los pesos no son optimos, pero aun asi siguen centrando la metodologia en `risk-engine-v1.1`.

Impacto: antes de capturas/defensa, conviene separar claramente "arquitectura evaluada" de "arquitectura predictiva final".

### Hallazgo RE-03

Clasificacion: NO CHANGE

No se detectaron textos peligrosos como "fraude confirmado", "transaccion fraudulenta" o "bloqueada por fraude". La interfaz y la documentacion usan lenguaje prudente: "no confirma fraude", "revision humana", "no bloquea operaciones".

## 5. ML Model Audit

### Hallazgo ML-01

Clasificacion: CRITICAL

El artefacto vigente `ml/artifacts/model_metadata.json` declara:

- `model_version`: `fraud-model-v1`.
- `algorithm`: `HistGradientBoostingClassifier`.
- `selected_model`: `Gradient Boosting`.
- `threshold`: `0.25`.
- dataset: `data/processed/remittances_analytics.csv`.
- split: `stratified 70/15/15`.

Esto no corresponde al modelo experimental final descrito:

- LightGBM.
- variables historicas derivadas del enfoque E3.
- threshold `0.9946945188209642`.
- PaySim.
- split temporal.

### Hallazgo ML-02

Clasificacion: CRITICAL

La pantalla `Inteligencia de riesgo` consume `/risk/ml/model-info` y `/risk/ml/metrics`, por lo que muestra el modelo anterior como modelo activo.

Impacto: no debe usarse esta pantalla actual como captura de resultados E5.

## 6. Dataset and Leakage Audit

### Hallazgo DATA-01

Clasificacion: CRITICAL

La documentacion vigente de ML usa el dataset sintetico interno de 10,000 registros:

- `docs/ml-methodology.md`.
- `docs/ml-evaluation.md`.
- `docs/data-sources.md`.
- `docs/data-dictionary.md`.
- `ml/artifacts/model_metadata.json`.

La investigacion final requiere PaySim:

- 6,362,620 transacciones.
- 8,213 fraudes.
- tasa aproximada 0.1291%.

No se encontro evidencia en el repo actual de PaySim, LightGBM o resultados E5.

### Hallazgo DATA-02

Clasificacion: IMPORTANT

La auditoria de leakage actual excluye variables del dataset sintetico interno, no las variables PaySim finales. No se encontro documentacion activa que confirme exclusion de:

- `newbalanceOrig`.
- `newbalanceDest`.
- `isFlaggedFraud`.
- `nameOrig`.
- `nameDest`.

Impacto: para defensa, debe existir evidencia visible de que esas variables no se usaron como predictores directos.

## 7. Threshold Audit

### Hallazgo TH-01

Clasificacion: CRITICAL

Threshold activo encontrado:

- `0.25` en `ml/artifacts/model_metadata.json`.
- `0.25` en `ml/artifacts/model_metrics.json`.
- `0.25` en `ml/artifacts/risk_engine_metadata.json`.
- `0.25` expuesto por `frontend/src/main.tsx` en `RiskIntelligenceView`.

Threshold academico final esperado:

- `0.9946945188209642`.

No debe recalcularse ni optimizarse con TEST. En esta auditoria solo se reporta la diferencia.

## 8. E5 Results Audit

### Resultados finales esperados

- TEST rows: 955,744.
- Fraudes: 4,010.
- No fraudes: 951,734.
- PR-AUC: 0.8817398533.
- ROC-AUC: 0.9985372055.
- Precision: 0.9674796748.
- Recall: 0.6825436409.
- F1: 0.8004094166.
- TP: 2,737.
- FP: 92.
- TN: 951,642.
- FN: 1,273.
- Predicted positive: 2,829.

### Hallazgo E5-01

Clasificacion: CRITICAL

No se encontraron estos resultados E5 en frontend, backend, docs, reports ni artifacts.

La pantalla actual muestra metricas anteriores de Gradient Boosting:

- Precision: 0.6286.
- Recall: 0.4000.
- F1: 0.4889.
- ROC-AUC: 0.8116.
- PR-AUC: 0.4728.
- Matrix: TN 1432, FP 13, FN 33, TP 22.

Impacto: las capturas academicas no deben tomarse aun desde la pantalla actual de `Inteligencia de riesgo`.

## 9. Frontend Audit

| Pantalla | Ruta / vista | Clasificacion academica | Estado |
|---|---|---|---|
| Login | `LandingLogin`, vista anonima | COMPLEMENTARIA | Muestra prototipo visual, pero no eje de riesgo. |
| Registro | `RegisterPanel` | COMPLEMENTARIA | Flujo de acceso; no eje academico. |
| Dashboard principal | `Dashboard` | COMPLEMENTARIA | Operacion del prototipo; no muestra IA/riesgo. |
| Envio de remesa | `NewRemittanceView` | CENTRAL | Sirve para generar/seleccionar operacion a evaluar. |
| Recepcion | `HistoryView`/recepcion | COMPLEMENTARIA | Flujo operativo. |
| Historial | `HistoryView` | COMPLEMENTARIA | Evidencia de operaciones. |
| Tracking | `TrackingView` | COMPLEMENTARIA | Trazabilidad operativa, no IA. |
| Risk Engine / Inteligencia de riesgo | `RiskIntelligenceView` | CENTRAL | Pantalla clave, pero desactualizada frente a E5. |
| Revision de riesgo | `RiskReviewView` | CENTRAL | Evidencia human-in-the-loop y explicabilidad. |
| Analitica | `AnalyticsView` | CENTRAL | Evidencia de analitica descriptiva, no E5. |
| Business Intelligence | `BusinessIntelligenceView` | COMPLEMENTARIA | Util para contexto, no resultado central. |
| Machine Learning | No hay pantalla separada | CENTRAL faltante | Debe resolverse como Research / Model Performance. |
| Forecasting | `ForecastingView` | COMPLEMENTARIA | Correctamente advierte que no modifica riesgo. |
| Blockchain | `BlockchainView` | COMPLEMENTARIA | Integridad/trazabilidad, no eje predictivo. |
| Marketplace | `MarketplaceView` | FUERA DEL EJE ACADEMICO | Puede distraer; evitar en defensa salvo mencion breve. |
| Asistente | `AssistantView` | COMPLEMENTARIA | Apoyo informativo, no resultado central. |
| Administracion/Soporte | `SupportUsersView` | FUERA DEL EJE ACADEMICO | No incluir en capturas academicas de riesgo. |

### Hallazgo FE-01

Clasificacion: IMPORTANT

El menu muestra muchas funciones complementarias junto a las centrales. Para defensa conviene preparar un recorrido enfocado y no navegar por Marketplace, Soporte o Blockchain salvo que el tutor lo solicite.

### Hallazgo FE-02

Clasificacion: IMPORTANT

El login dice "Plataforma para gestionar beneficiarios, cotizar envios, crear remesas y consultar historial." No contradice directamente el alcance, pero para capturas academicas seria mejor reforzar visualmente "prototipo academico".

## 10. Explainability Audit

### Estado actual

Clasificacion: NO CHANGE / IMPORTANT

Fortalezas:

- `RiskReviewView` muestra score final, banda, accion, reglas activadas, explicaciones, versiones y decision humana.
- `RiskIntelligenceView` muestra variables relevantes, comparacion de modelos y matriz de confusion.
- Los textos evitan afirmar fraude confirmado.

Brechas:

- La explicabilidad actual corresponde a la arquitectura previa, no a LightGBM/E5.
- No muestra variables relevantes del modelo final E5.
- No muestra explicitamente threshold final ni dataset PaySim.

### Textos peligrosos

No se encontraron textos exactos:

- "Fraude detectado".
- "Transaccion fraudulenta".
- "Fraude confirmado".
- "Bloqueada por fraude".

## 11. Disclaimer Audit

### Disclaimer general

Clasificacion: NO CHANGE

Existe disclaimer general visible en frontend:

> FIDUCIA es un prototipo tecnologico desarrollado con fines educativos y de investigacion. No constituye una entidad financiera ni un servicio real de remesas.

Tambien aparece en README y documentos academicos.

### Disclaimer E5 / PaySim

Clasificacion: CRITICAL

No se encontro una advertencia visible equivalente a:

"Resultados experimentales obtenidos sobre el dataset sintetico PaySim. No representan desempeno validado sobre remesas reales de Guatemala."

Esta advertencia debe existir en cualquier pantalla academica donde se muestren metricas E5.

## 12. Academic Screen / Model Performance

### Hallazgo MP-01

Clasificacion: CRITICAL

No existe actualmente una pantalla academica dedicada a:

- Research.
- Model Performance.
- Experimental Results.
- E5 Results.

La pantalla `Inteligencia de riesgo` no cumple este papel porque usa resultados anteriores.

### Recomendacion de implementacion

Crear una pantalla `Research / Model Performance` o equivalente que muestre:

- Dataset: PaySim.
- Total rows: 6,362,620.
- Frauds: 8,213.
- Final model: LightGBM.
- TRAIN / VALIDATION / TEST temporal.
- Threshold: `0.9946945188209642`.
- PR-AUC: `0.8817`.
- ROC-AUC: `0.9985`.
- Precision: `96.75%`.
- Recall: `68.25%`.
- F1: `80.04%`.
- Confusion Matrix: TP 2737, FP 92, TN 951642, FN 1273.
- Disclaimer PaySim.

No se implemento en esta ejecucion por restriccion expresa.

## 13. Recommended Screenshots

### CAPTURA 1

Pantalla exacta: Login / Landing  
Ruta frontend: `LandingLogin`  
Que debe verse: logo Fiducia, acceso seguro, disclaimer de prototipo.  
Objetivo academico: demostrar Fiducia como prototipo tecnologico.  
Lista actualmente: PARCIAL.  
Necesita modificacion: si, reforzar disclaimer academico en zona visible si se usara como captura.

### CAPTURA 2

Pantalla exacta: Enviar remesa  
Ruta frontend: `NewRemittanceView`  
Que debe verse: creacion/cotizacion de una operacion digital de remesa.  
Objetivo academico: demostrar unidad de analisis transaccional.  
Lista actualmente: SI.  
Necesita modificacion: no critica.

### CAPTURA 3

Pantalla exacta: Detalle de remesa  
Ruta frontend: `TransactionDetailView`  
Que debe verse: identificador, monto, pais origen/destino, estado y datos operativos.  
Objetivo academico: evidenciar transaccion evaluable por riesgo.  
Lista actualmente: SI.  
Necesita modificacion: no critica.

### CAPTURA 4

Pantalla exacta: Revision de riesgo  
Ruta frontend: `RiskReviewView`  
Que debe verse: LOW / MEDIUM / HIGH, score, accion recomendada, reglas activadas y explicacion.  
Objetivo academico: demostrar clasificacion, explicabilidad y human-in-the-loop.  
Lista actualmente: PARCIAL.  
Necesita modificacion: si, asegurar que versiones/threshold correspondan a arquitectura final.

### CAPTURA 5

Pantalla exacta: Inteligencia de riesgo  
Ruta frontend: `RiskIntelligenceView`  
Que debe verse: modelo activo, metricas, variables relevantes, matriz de confusion.  
Objetivo academico: demostrar evaluacion cuantitativa.  
Lista actualmente: NO para documento final.  
Necesita modificacion: si, hoy muestra modelo/metrica antigua.

### CAPTURA 6

Pantalla exacta: Research / Model Performance  
Ruta frontend: no existe actualmente.  
Que debe verse: PaySim, LightGBM, split temporal, threshold final, E5 metrics, confusion matrix y disclaimer.  
Objetivo academico: demostrar OE4 y resultados experimentales.  
Lista actualmente: NO.  
Necesita modificacion: si, implementacion requerida.

### CAPTURA 7

Pantalla exacta: Analitica  
Ruta frontend: `AnalyticsView`  
Que debe verse: indicadores descriptivos de operaciones.  
Objetivo academico: demostrar analitica de datos aplicada.  
Lista actualmente: SI.  
Necesita modificacion: no critica.

### CAPTURA 8

Pantalla exacta: Blockchain o Forecasting, elegir una sola si aporta valor  
Ruta frontend: `BlockchainView` o `ForecastingView`  
Que debe verse: trazabilidad/integridad o analitica predictiva complementaria.  
Objetivo academico: mostrar componente complementario, no resultado central.  
Lista actualmente: SI.  
Necesita modificacion: no critica, pero debe presentarse como complementario.

## 14. Defense Demo Flow

Duracion objetivo: aproximadamente 2 minutos.

1. Login rapido con perfil autorizado.
2. Ir directamente a una remesa existente o crear una remesa de prueba.
3. Abrir evaluacion de riesgo.
4. Mostrar banda LOW / MEDIUM / HIGH y explicar que no significa fraude confirmado.
5. Mostrar reglas activadas, score ML, senal de anomalia y recomendacion de revision.
6. Abrir `Research / Model Performance` cuando exista.
7. Mostrar PaySim, LightGBM, threshold congelado y resultados E5.
8. Cerrar con disclaimer: resultados experimentales sobre PaySim, no validacion sobre remesas reales de Guatemala.

Evitar en la demo principal:

- Marketplace.
- Administracion de soporte.
- Recorrido completo por beneficiarios/metodos de pago.
- Blockchain salvo mencion final opcional.
- Forecasting salvo mencion final opcional.

## 15. Required Changes

### CRITICAL

1. Actualizar la capa academica visible para reflejar PaySim, LightGBM, split temporal y E5.
2. Evitar que `risk-engine-v1.1` 30/50/20 aparezca como arquitectura predictiva final.
3. Sustituir o separar visualmente metricas antiguas de Gradient Boosting threshold 0.25.
4. Crear pantalla `Research / Model Performance`.
5. Agregar disclaimer PaySim/E5 en pantalla academica de resultados.
6. Alinear threshold mostrado con `0.9946945188209642` en la configuracion academica final.

### IMPORTANT

1. Reetiquetar componentes complementarios para que no compitan con el eje academico.
2. Actualizar documentacion tecnica antes de usarla como anexo.
3. Preparar capturas solo despues de resolver la pantalla E5.
4. Mantener Marketplace fuera de la defensa central.
5. Reforzar en login/dashboard que Fiducia es prototipo academico, si esas pantallas se usaran como evidencia visual.

## 16. Optional Improvements

1. Crear modo "Demo academica" con navegacion reducida.
2. Agregar una tarjeta visual de "Arquitectura final" con ML como componente predictivo principal.
3. Agregar glosario: riesgo alto, revision manual, falso positivo, falso negativo, PR-AUC y threshold.
4. Agregar export de resultados E5 para anexos.
5. Agregar badge "Complementario" en Forecasting, Blockchain, Assistant y Marketplace.

## 17. Components That Must Not Be Modified

En una siguiente fase de correccion, no modificar sin autorizacion:

- Resultados E5.
- Threshold final `0.9946945188209642`.
- Split temporal aprobado.
- Matriz de confusion E5.
- Dataset PaySim original.
- Variables excluidas por leakage.
- Modelos o artefactos sin protocolo.
- Risk Engine historico si se conserva como arquitectura evaluada.

## 18. Final Recommendation

No tomar todavia las capturas academicas finales.

Primero debe implementarse o preparar visualmente una pantalla academica de resultados E5 y separar la arquitectura evaluada `risk-engine-v1.1` de la arquitectura predictiva final basada en LightGBM.

Una vez corregidas las brechas CRITICAL, las capturas deben centrarse en:

- Prototipo.
- Flujo de remesa.
- Evaluacion de riesgo.
- Explicabilidad.
- Resultados E5.
- Disclaimer PaySim.

## Findings Summary

CRITICAL: 9  
IMPORTANT: 7  
OPTIONAL: 5  
NO CHANGE: 3

## Critical and Important Findings To Resolve Before Academic Screenshots

### CRITICAL

1. El modelo activo sigue siendo `fraud-model-v1` / `HistGradientBoostingClassifier`, no LightGBM final.
2. El threshold activo sigue siendo `0.25`, no `0.9946945188209642`.
3. Las metricas visibles corresponden al experimento anterior, no a E5.
4. No existe pantalla `Research / Model Performance`.
5. No aparece disclaimer PaySim/E5 junto a resultados finales.
6. El Risk Engine activo usa pesos `30/50/20`.
7. La documentacion tecnica vigente sigue basada en dataset sintetico interno de 10,000 registros.
8. No se encontro evidencia visible de split temporal PaySim TRAIN/VALIDATION/TEST.
9. No se encontro evidencia visible de exclusion de variables PaySim con leakage en la configuracion final.

### IMPORTANT

1. La pantalla `Inteligencia de riesgo` no debe capturarse aun como evidencia final.
2. `docs/risk-engine-card.md`, `docs/ml-methodology.md` y `docs/ml-evaluation.md` requieren actualizacion antes de anexarse.
3. El menu principal mezcla funciones centrales con complementarias y fuera del eje academico.
4. Marketplace debe mantenerse fuera del recorrido principal de defensa.
5. Login/dashboard podrian reforzar mas visiblemente el caracter de prototipo academico.
6. La explicabilidad actual es buena, pero corresponde a la arquitectura previa.
7. Las capturas deben esperar a que E5 este representado correctamente.

