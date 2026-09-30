# Indice de evidencia inicial

Fecha de creacion: 2026-09-30  
Estado: PENDING_REVIEW  
Nota: este indice registra evidencia existente observada en el repositorio. No implica aprobacion academica.

## Evidencia tecnologica

| ID | Evidencia | Ruta | Tipo | Estado | Uso academico potencial | Observaciones |
|---|---|---|---|---|---|---|
| EV-TECH-001 | Inventario final del sistema | `docs/system-inventory.md` | Documentacion tecnica | EXISTING | Describir arquitectura y componentes reutilizables. | Requiere actualizar si se consolidan cambios recientes. |
| EV-TECH-002 | Arquitectura general | `docs/architecture.md` | Documentacion tecnica | EXISTING | Explicar Fiducia como prototipo. | Contiene fases 1-10. |
| EV-TECH-003 | API documentada | `docs/api.md` | Documentacion tecnica | EXISTING | Anexo tecnico / evidencia de implementacion. | Debe mantenerse sincronizada. |
| EV-TECH-004 | Pruebas automatizadas backend | `backend/tests/*` | Codigo/test | EXISTING | Evidencia de regresion y reproducibilidad tecnica. | Registrar comandos y fecha de ejecucion academica en fase posterior. |
| EV-TECH-005 | Validacion final previa | `reports/final/final_validation.json` | Reporte tecnico | EXISTING | Evidencia de salud del sistema. | Generado 2026-09-01. |
| EV-TECH-006 | Resumen de pruebas previo | `reports/final/test_summary.json` | Reporte tecnico | EXISTING | Evidencia de pruebas y build. | Generado 2026-09-01; puede estar desactualizado frente a cambios recientes. |

## Evidencia de datos

| ID | Evidencia | Ruta | Tipo | Estado | Uso academico potencial | Observaciones |
|---|---|---|---|---|---|---|
| EV-DATA-001 | Dataset sintetico | `data/synthetic/remittances_synthetic.csv` | Datos sinteticos | EXISTING | Demo, EDA y experimentos controlados. | No representa datos reales de Guatemala. |
| EV-DATA-002 | Dataset procesado analitico | `data/processed/remittances_analytics.csv` | Datos procesados | EXISTING | Entrenamiento/evaluacion ML. | Hash en `reports/final/dataset-checksums.json`. |
| EV-DATA-003 | Diccionario de datos | `docs/data-dictionary.md` | Documentacion de datos | EXISTING | Marco metodologico de variables. | Debe vincularse a dataset manifest academico. |
| EV-DATA-004 | Pipeline de datos | `docs/data-pipeline.md`, `scripts/data_pipeline.py` | Script/documentacion | EXISTING | Reproducibilidad. | Falta manifest academico formal. |
| EV-DATA-005 | Fuentes de datos | `docs/data-sources.md` | Documentacion | EXISTING | Separar datos sinteticos, internos y externos. | No se descargaron datasets externos en Fase 3. |

## Evidencia ML y Risk Engine

| ID | Evidencia | Ruta | Tipo | Estado | Uso academico potencial | Observaciones |
|---|---|---|---|---|---|---|
| EV-ML-001 | Metodologia ML | `docs/ml-methodology.md` | Documentacion tecnica | EXISTING | Base para metodologia computacional. | Requiere lenguaje academico y citas. |
| EV-ML-002 | Evaluacion ML | `docs/ml-evaluation.md` | Resultados tecnicos | EXISTING | Resultados iniciales por modelo. | Usa datos sinteticos. |
| EV-ML-003 | Comparacion de modelos | `reports/ml/model_comparison.json` | Reporte tecnico | EXISTING | Tabla de metricas y seleccion de modelo. | Necesita registro en experiment registry posterior. |
| EV-ML-004 | EDA ML | `reports/ml/eda_summary.json` | Reporte tecnico | EXISTING | Caracterizacion inicial del dataset. | Datos sinteticos. |
| EV-ML-005 | Artefacto modelo fraude | `ml/artifacts/fraud_model.joblib` | Modelo | EXISTING | Prototipo funcional. | Hash en `reports/final/model-artifact-checksums.json`. |
| EV-RISK-001 | Metodologia Risk Engine | `docs/risk-engine-methodology.md` | Documentacion tecnica | EXISTING | Diseno hibrido Rules + ML + Anomaly. | Pesos declarados como baseline heuristico. |
| EV-RISK-002 | Evaluacion Risk Engine | `docs/risk-engine-evaluation.md` | Resultados tecnicos | EXISTING | Evaluacion del sistema hibrido. | No debe ocultar que ML only supera algunas metricas. |
| EV-RISK-003 | Ablation study | `reports/risk_engine/ablation_results.json` | Reporte tecnico | EXISTING | Comparacion de componentes. | Util para discusion. |
| EV-RISK-004 | Modelo anomalias | `ml/artifacts/anomaly_model.joblib`, `reports/risk_engine/anomaly_evaluation.json` | Modelo/reporte | EXISTING | Complemento de deteccion atipica. | Entrenamiento no supervisado. |

## Evidencia complementaria

| ID | Evidencia | Ruta | Tipo | Estado | Uso academico potencial | Observaciones |
|---|---|---|---|---|---|---|
| EV-FORE-001 | Metodologia forecasting | `docs/forecasting-methodology.md` | Documentacion | EXISTING | Componente complementario de analitica. | No eje principal. |
| EV-FORE-002 | Evaluacion forecasting | `docs/forecasting-evaluation.md`, `reports/forecasting/*` | Reportes | EXISTING | Analitica predictiva complementaria. | Usar solo si responde a objetivos aprobados. |
| EV-BI-001 | Metodologia BI | `docs/bi-methodology.md` | Documentacion | EXISTING | Dashboard analitico complementario. | Read-only. |
| EV-BC-001 | Metodologia blockchain | `docs/blockchain-methodology.md` | Documentacion | EXISTING | Evidencia tecnologica complementaria. | No atribuir mejora de riesgo sin evidencia. |
| EV-ASST-001 | Documentacion asistente | `docs/assistant-*` | Documentacion | EXISTING | Soporte/demo y seguridad. | No eje principal. |

## Evidencia pendiente

| ID | Evidencia pendiente | Motivo | Prioridad |
|---|---|---|---|
| EV-PEND-001 | Fuentes academicas verificadas | Necesarias para marco teorico y estado del arte. | Alta |
| EV-PEND-002 | Fuentes oficiales de Guatemala sobre remesas | Necesarias para contexto nacional. | Alta |
| EV-PEND-003 | Dataset manifest academico | Necesario para trazabilidad y reproducibilidad. | Alta |
| EV-PEND-004 | Experiment registry academico | Necesario para no sobrescribir experimentos. | Alta |
| EV-PEND-005 | Leakage analysis academico | Necesario para defensa metodologica. | Alta |
| EV-PEND-006 | Guion de demo academica normal/anomala/alto riesgo | Necesario para defensa. | Media |

## Evidencia academica Modulo 1

| ID | Evidencia | Ruta | Tipo | Estado | Uso academico potencial | Observaciones |
|---|---|---|---|---|---|---|
| EV-M1-001 | Tema de investigacion y alternativa | `research/01_anteproyecto/tema.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Validacion inicial del titulo. | No aprobado por tutor. |
| EV-M1-002 | Situacion problematica | `research/01_anteproyecto/problema.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Base del planteamiento del problema. | Contiene citas pendientes. |
| EV-M1-003 | Pregunta de investigacion | `research/01_anteproyecto/pregunta.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Revision de Version A y Version B. | No elegir automaticamente. |
| EV-M1-004 | Delimitaciones | `research/01_anteproyecto/delimitacion.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Delimitacion temporal, espacial y unidad de analisis. | Fechas pendientes. |
| EV-M1-005 | Objetivos | `research/01_anteproyecto/objetivos.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Objetivo general y cuatro especificos. | Secuencia logica documentada. |
| EV-M1-006 | Justificaciones | `research/01_anteproyecto/justificacion.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Sustento teorico, metodologico y practico/social. | Requiere fuentes verificables. |
| EV-M1-007 | Anteproyecto integrado | `research/01_anteproyecto/anteproyecto.md` | Documento academico | DRAFT / PENDING_TUTOR_REVIEW | Documento principal de Modulo 1. | Incluye revision cruzada de coherencia. |
