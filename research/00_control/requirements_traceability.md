# Matriz de trazabilidad academica

Fecha de creacion: 2026-09-30  
Estado: PENDING_TUTOR_REVIEW  
Nota: esta matriz es inicial. No contiene resultados ni conclusiones aprobadas.

## Elementos rectores provisionales

| Elemento | Contenido | Estado |
|---|---|---|
| Tema | Aplicacion de Inteligencia Artificial y Analitica de Datos para la identificacion del riesgo transaccional en remesas digitales: diseno y validacion de un prototipo aplicado al contexto guatemalteco. | PROPOSED / PENDING_TUTOR_REVIEW |
| Tema alternativo | Diseno y evaluacion de un prototipo basado en Inteligencia Artificial y Analitica de Datos para apoyar la identificacion del riesgo transaccional en operaciones digitales de remesas en el contexto guatemalteco. | PROPOSED_FOR_TUTOR_REVIEW |
| Pregunta A | Como puede la aplicacion de Inteligencia Artificial y Analitica de Datos contribuir a la identificacion del riesgo transaccional en operaciones digitales de remesas aplicadas al contexto guatemalteco? | PENDING_TUTOR_REVIEW |
| Pregunta B | De que manera un prototipo basado en Inteligencia Artificial y Analitica de Datos puede apoyar la identificacion del riesgo transaccional en operaciones digitales de remesas, considerando su aplicacion experimental al contexto guatemalteco? | PROPOSED_FOR_TUTOR_REVIEW |
| Objetivo general | Disenar y evaluar un prototipo basado en Inteligencia Artificial y Analitica de Datos para apoyar la identificacion del riesgo transaccional en operaciones digitales de remesas aplicadas al contexto guatemalteco. | PENDING_TUTOR_REVIEW |

## Trazabilidad Modulo 1

| Requisito Modulo 1 | Archivo | Estado | Observacion |
|---|---|---|---|
| Tema de investigacion | `research/01_anteproyecto/tema.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Incluye version actual y alternativa. |
| Situacion problematica | `research/01_anteproyecto/problema.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Construida desde remesas, digitalizacion, riesgo e IA; no desde Fiducia. |
| Pregunta de investigacion | `research/01_anteproyecto/pregunta.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Incluye Version A y Version B. |
| Delimitacion temporal | `research/01_anteproyecto/delimitacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Distingue periodo de investigacion y periodo de datos. |
| Delimitacion espacial | `research/01_anteproyecto/delimitacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Guatemala como contexto principal; limita representatividad del dataset. |
| Unidad de analisis | `research/01_anteproyecto/delimitacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Transacciones financieras digitales. |
| Objetivo general | `research/01_anteproyecto/objetivos.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Mantiene verbo disenar y evaluar. |
| Cuatro objetivos especificos | `research/01_anteproyecto/objetivos.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Secuencia analizar, disenar, implementar, evaluar. |
| Justificacion teorica | `research/01_anteproyecto/justificacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Requiere fuentes verificables. |
| Justificacion metodologica | `research/01_anteproyecto/justificacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | No cierra Modulo 3. |
| Justificacion practica/social | `research/01_anteproyecto/justificacion.md`, `research/01_anteproyecto/anteproyecto.md` | DRAFT / PENDING_TUTOR_REVIEW | Usa lenguaje potencial, sin prometer impacto real. |

## Trazabilidad inicial

| Pregunta de investigacion | Objetivo | Variable o dimension | Fuente de datos | Tecnica | Experimento | Metrica | Resultado | Conclusion |
|---|---|---|---|---|---|---|---|---|
| Como puede la aplicacion de IA y Analitica de Datos contribuir a identificar riesgo transaccional en remesas digitales? | OE1: Analizar factores, patrones y variables asociados al riesgo transaccional. | Factores de riesgo, patrones transaccionales, variables historicas y conductuales. | `data/processed/remittances_analytics.csv`; literatura pendiente de validar; fuentes oficiales pendientes. | Revision documental; analisis exploratorio; diccionario de datos. | EDA sintetico existente en `reports/ml/eda_summary.json`; revision academica pendiente. | Distribucion de clase, resumen de variables, correlaciones o importancia descriptiva pendientes. | PARTIAL: existe EDA tecnica sobre datos sinteticos. | PENDIENTE DE OBTENER / VALIDAR. |
| Como puede la aplicacion de IA y Analitica de Datos contribuir a identificar riesgo transaccional en remesas digitales? | OE2: Disenar un modelo analitico que combine reglas de negocio y Machine Learning. | Score de reglas, probabilidad ML, score de anomalia, score final. | `backend/app/risk/*`; `ml/artifacts/*`; `docs/risk-engine-methodology.md`. | Diseno hibrido rule-based + supervised ML + anomaly detection. | Ablation study existente en `reports/risk_engine/ablation_results.json`. | Precision, Recall, F1, ROC-AUC, PR-AUC, matriz de confusion. | PARTIAL: Risk Engine funcional con resultados tecnicos. | PENDIENTE DE ANALISIS ACADEMICO. |
| Como puede la aplicacion de IA y Analitica de Datos contribuir a identificar riesgo transaccional en remesas digitales? | OE3: Implementar el modelo propuesto dentro del prototipo Fiducia. | Integracion API, persistencia de risk assessments, explicabilidad, revision humana. | Codigo backend/frontend; tests `test_phase5_risk_engine.py`; docs de arquitectura. | Implementacion de prototipo; pruebas automatizadas; demo controlada. | Evaluacion de remesa normal/anomala/alto riesgo pendiente de guion academico. | Estado funcional, cobertura de pruebas, evidencia de endpoints. | PARTIAL: implementacion existe. | PENDIENTE DE DEMOSTRACION FORMAL. |
| Como puede la aplicacion de IA y Analitica de Datos contribuir a identificar riesgo transaccional en remesas digitales? | OE4: Evaluar desempeno del modelo mediante metricas y analisis de resultados. | Desempeno predictivo, falsos positivos, falsos negativos, limitaciones. | `reports/ml/model_comparison.json`; `docs/ml-evaluation.md`; `reports/risk_engine/*`. | Comparacion de baseline y modelos; validacion/test; ablation. | DummyClassifier, Logistic Regression, Random Forest, Gradient Boosting, Risk Engine. | Precision, Recall, F1, ROC-AUC, PR-AUC, confusion matrix, FPR/FNR pendientes de consolidar. | PARTIAL: resultados tecnicos existen. | PENDIENTE DE DISCUSION Y CONCLUSIONES. |

## Observaciones de control

- Ninguna conclusion esta aprobada.
- Ninguna metrica debe presentarse como evidencia final sin documentar dataset, version, seed y fecha de ejecucion.
- Los datos disponibles son sinteticos salvo evidencia posterior en contrario.
- Blockchain, forecasting, asistente y marketplace son componentes complementarios y no deben desplazar el eje de riesgo transaccional sin aprobacion del tutor.
- Los resultados tecnicos existentes se mantienen como evidencia preliminar; no son resultados finales del Proyecto Final de Grado.
