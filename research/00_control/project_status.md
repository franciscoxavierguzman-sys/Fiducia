# Estado del proyecto - Auditoria inicial

Fecha de auditoria: 2026-09-30  
Estado general: PROPOSED / PENDING_TUTOR_REVIEW  
Alcance: primera ejecucion del prompt maestro academico.  
Restriccion aplicada: no se modificaron modelos, Risk Engine, base de datos, frontend ni logica funcional.

## A. Estado tecnologico actual

| Componente | Estado | Evidencia observada | Comentario |
|---|---|---|---|
| Frontend | FUNCTIONAL | `frontend/src/main.tsx`, `frontend/package.json`, `npm run build` reportado previamente como PASS | React 19, Vite, Tailwind y lucide-react. Incluye vistas de remesas, riesgo, analitica, blockchain, asistente, soporte y marketplace. |
| Backend | FUNCTIONAL | `backend/app/main.py`, `backend/app/api/v1/router.py`, `reports/final/final_validation.json` | FastAPI con routers versionados `/api/v1`, health y ready. |
| Base de datos | FUNCTIONAL | `backend/app/models/*`, `backend/app/db/session.py`, `backend/app/db/sqlite_migrations.py` | SQLAlchemy con SQLite local y compatibilidad inicial para PostgreSQL por `psycopg2-binary`. |
| Autenticacion | FUNCTIONAL | `backend/app/api/v1/endpoints/auth.py`, `backend/app/security/*`, `backend/tests/test_auth.py` | Registro, login JWT, recuperacion de contrasena y cambio obligatorio. |
| Usuarios y soporte | FUNCTIONAL | `backend/app/api/v1/endpoints/users.py`, `backend/tests/test_support_users.py` | Incluye rol SUPPORT para administrar usuarios, reiniciar contrasenas y bloquear/desbloquear. |
| Transacciones/remesas | FUNCTIONAL | `backend/app/api/v1/endpoints/transactions.py`, `backend/app/services/remittances.py`, `backend/tests/test_remittances.py` | Simulacion, creacion, remesas enviadas/recibidas, tracking y recepcion. |
| Risk Engine | FUNCTIONAL | `backend/app/services/risk_engine.py`, `backend/app/risk/*`, `docs/risk-engine-methodology.md` | Sistema hibrido Rules + ML + Anomaly con snapshots, explicabilidad y human-in-the-loop. |
| Machine Learning | FUNCTIONAL | `ml/artifacts/fraud_model.joblib`, `reports/ml/model_comparison.json`, `backend/tests/test_phase4_ml.py` | Modelo `fraud-model-v1`, comparacion con baseline y metricas. Usa datos sinteticos. |
| Datasets | PARTIAL | `data/synthetic/remittances_synthetic.csv`, `data/processed/remittances_analytics.csv`, `docs/data-dictionary.md` | Datos sinteticos documentados; faltan manifiestos academicos formales, licencia/origen externo y validacion con tutor. |
| Forecasting | FUNCTIONAL | `backend/app/services/forecasting.py`, `docs/forecasting-methodology.md`, `reports/forecasting/*` | Modelo `remittance-forecast-v1` separado del Risk Engine. Complementario, no eje principal. |
| Blockchain | FUNCTIONAL | `backend/app/blockchain/*`, `docs/blockchain-methodology.md`, `backend/tests/test_phase8_blockchain.py` | Evidencia local SHA-256 y proof-of-work demostrativo. Complementario al eje academico. |
| Business Intelligence | FUNCTIONAL | `backend/app/bi/*`, `docs/bi-methodology.md`, `backend/tests/test_phase7_business_intelligence.py` | KPIs read-only sobre datos operacionales y riesgo. |
| Dashboards | FUNCTIONAL | `frontend/src/main.tsx`, endpoints `analytics`, `bi`, `risk`, `forecasting`, `blockchain` | Existen dashboards tecnicos/comerciales; falta dashboard academico Research / Model Performance. |
| APIs | FUNCTIONAL | `backend/app/api/v1/router.py`, `docs/api.md` | API modular con autenticacion y roles. |
| Testing | FUNCTIONAL | `backend/tests/*`, `reports/final/test_summary.json` | Evidencia previa: backend final 89 passed, luego suite local reciente reportada por Codex 106 passed; requiere registrar ejecuciones academicas reproducibles. |
| Documentacion tecnica | FUNCTIONAL | `docs/*.md`, `README.md` | Amplia documentacion por fases. Falta convertirla a estructura academica por modulos PBS. |
| Marketplace | FUNCTIONAL / SECONDARY | `backend/app/api/v1/endpoints/marketplace.py`, `backend/tests/test_marketplace.py` | Funcionalidad reciente, secundaria respecto al objetivo academico de riesgo transaccional. |
| Asistente | FUNCTIONAL / SECONDARY | `backend/app/assistant/*`, `docs/assistant-*` | Read-only, util para demo y soporte, no eje metodologico principal. |

## B. Estado academico por modulo PBS

| Modulo PBS | Elementos existentes reutilizables | Estado academico | Observaciones |
|---|---|---|---|
| Modulo 1: Anteproyecto | `research/01_anteproyecto/*`, README, docs por fases, problema implicito de riesgo transaccional, disclaimer | DRAFT / PENDING_TUTOR_REVIEW | Se redacto propuesta inicial de tema, problema, pregunta, delimitaciones, objetivos y justificaciones. Falta revision del tutor y fuentes verificadas. |
| Modulo 2: Marco teorico | `docs/data-sources.md`, `docs/ml-methodology.md`, `docs/risk-engine-methodology.md` | PARTIAL | Hay conceptos tecnicos, pero faltan fuentes academicas verificadas, antecedentes nacionales/internacionales y matriz de literatura. |
| Modulo 3: Metodologia | `docs/ml-methodology.md`, `docs/data-pipeline.md`, `docs/forecasting-methodology.md` | PARTIAL | Hay metodologia tecnica; falta diseno metodologico academico, unidad de analisis, instrumentos, validez, etica y cronograma. |
| Modulo 4: Trabajo de campo y resultados | `reports/ml/*`, `reports/risk_engine/*`, `reports/forecasting/*`, `reports/final/*` | PARTIAL | Existen resultados computacionales, pero deben ordenarse por objetivos, evidencia y limitaciones. |
| Modulo 5: Documento final y defensa | `docs/demo-script.md`, `docs/demo-scenario.md`, `docs/final-limitations.md` | PARTIAL | Hay material de demo; faltan documento final academico, defensa, anexos y preguntas del jurado. |

## C. Gap Analysis

| Requisito PBS | Estado actual | Evidencia existente | Brecha | Accion requerida | Prioridad |
|---|---|---|---|---|---|
| Situacion problematica | PARTIAL | README, docs de riesgo | No esta redactada formalmente ni sustentada con fuentes verificadas. | Redactar problema con fuentes oficiales y academicas. | Alta |
| Pregunta de investigacion | PROPOSED | Prompt maestro | Falta aprobacion del tutor. | Registrar como propuesta y validar. | Alta |
| Objetivo general | PROPOSED | Prompt maestro | Falta aprobacion del tutor. | Mantener trazabilidad con pregunta y metodologia. | Alta |
| Cuatro objetivos especificos | PROPOSED | Prompt maestro | Falta aprobacion del tutor. | Validar y mapear contra evidencia existente. | Alta |
| Justificacion teorica | NOT_IMPLEMENTED | N/A | No hay fuentes academicas verificadas suficientes. | Construir marco teorico con referencias reales. | Alta |
| Justificacion metodologica | PARTIAL | docs metodologicos tecnicos | Falta traducir a lenguaje academico y justificar diseno. | Preparar propuesta metodologica. | Alta |
| Justificacion practica/social | PARTIAL | README, disclaimer | Falta sustento contextual guatemalteco. | Incorporar fuentes oficiales y contexto de remesas. | Alta |
| Marco teorico | PARTIAL | docs tecnicos | Falta matriz de literatura, referencias verificadas y estado del arte. | Crear `references.csv` y `literature_matrix.csv` en fase posterior. | Alta |
| Diseno metodologico | PARTIAL | ML/data pipeline docs | Falta enfoque, tipo de estudio, unidad de analisis, validez y etica. | Redactar propuesta PENDING_TUTOR_REVIEW. | Alta |
| Datos | PARTIAL | data synthetic/processed, docs data | Falta dataset manifest academico, licencias, checksums y separacion formal raw/interim/processed/synthetic. | Crear manifiesto y leakage analysis en fase posterior. | Alta |
| Experimentos | PARTIAL | scripts, reports, tests | Falta registry academico de experimentos y criterio previo de seleccion final. | Crear `experiment_registry.csv` y versionar ejecuciones. | Alta |
| Resultados | PARTIAL | reports ML/risk/forecasting | Falta separar resultados de interpretacion y vincular a objetivos. | Construir seccion de resultados por objetivo. | Alta |
| Conclusiones | NOT_IMPLEMENTED | N/A | No deben generarse sin resultados academicos consolidados. | Crear matriz objetivo-resultado-evidencia-conclusion luego. | Media |
| Defensa | PARTIAL | docs demo | Falta guion academico, Q&A y hallazgos clave. | Preparar despues de validar resultados. | Media |

## D. Riesgos academicos identificados

| Riesgo | Descripcion | Evidencia / razon | Mitigacion |
|---|---|---|---|
| Fuentes insuficientes | La documentacion tecnica no equivale a marco teorico academico. | No existe `research/02_marco_teorico/references.csv`. | Construir referencias verificadas con DOI/URL reales. |
| Datos sinteticos | El dataset principal es sintetico y no representa necesariamente remesas reales de Guatemala. | `docs/data-sources.md` declara datos sinteticos; `docs/ml-evaluation.md` limita su uso. | Documentar supuestos, metodo de generacion y limitaciones. |
| Representatividad | No hay evidencia de que el dataset represente comportamiento transaccional guatemalteco real. | No se descargaron datasets externos en Fase 3. | Evitar afirmaciones de representatividad; buscar fuentes oficiales para contexto macro. |
| Posible leakage | Ya existe auditoria tecnica, pero debe formalizarse academicamente. | `docs/ml-methodology.md`, `backend/tests/test_phase4_ml.py`. | Crear `research/04_datos/leakage_analysis.md` en fase posterior. |
| Metricas incompletas para defensa | Existen precision, recall, F1, ROC-AUC, PR-AUC, matriz de confusion; falta explicacion academica por objetivo. | `reports/ml/model_comparison.json`, `docs/ml-evaluation.md`. | Relacionar metricas con pregunta y objetivos. |
| Reproducibilidad no centralizada | Hay scripts, seeds y checksums, pero no registry academico consolidado. | `reports/final/*checksums.json`, scripts. | Crear dataset manifest y experiment registry. |
| Confusion entre prototipo y servicio real | La app simula remesas y marketplace; podria interpretarse como producto financiero. | README disclaimer y docs security. | Mantener disclaimer visible en investigacion y defensa. |
| Blockchain fuera del eje | Blockchain existe, pero no responde directamente al riesgo transaccional ML. | `docs/blockchain-methodology.md`. | Mantenerlo como componente complementario, no objetivo central. |
| Marketplace fuera del eje | Marketplace aporta funcionalidad, pero no a la cadena principal del problema de riesgo. | Modulo marketplace reciente. | Tratarlo como secundario/demo, no evidencia central. |
| Aprobacion del tutor | Tema, pregunta, objetivos y metodologia son propuestas. | Prompt maestro indica pendiente. | Registrar todo como PENDING_TUTOR_REVIEW. |

## E. Plan de adaptacion recomendado

| Fase | Objetivo | Acciones | Entregables esperados |
|---|---|---|---|
| 1. Control academico | Ordenar trazabilidad y evidencia | Mantener `research/00_control`, registrar decisiones, evidencia y brechas. | Matriz de trazabilidad viva y evidencia indexada. |
| 2. Anteproyecto | Formalizar Modulo 1 | Redactar problema, pregunta, objetivos, delimitaciones y justificaciones. | `research/01_anteproyecto/*` creado como DRAFT / PENDING_TUTOR_REVIEW. |
| 3. Marco teorico | Sustentar con fuentes verificadas | Buscar y registrar fuentes reales sobre remesas, IA financiera, fraude, AML, ML y explicabilidad. | `references.csv`, `literature_matrix.csv`, borrador marco teorico. |
| 4. Metodologia | Convertir pipeline tecnico en diseno academico | Definir enfoque, unidad de analisis, datos, experimentos, etica, validez y cronograma. | Propuesta metodologica PENDING_TUTOR_REVIEW. |
| 5. Datos y reproducibilidad | Formalizar datasets | Crear manifiesto, checksums, leakage analysis y versionado de datasets. | `dataset_manifest.csv`, `leakage_analysis.md`. |
| 6. Experimentos | Registrar modelos y resultados | Consolidar baseline, modelos, thresholds, metricas y limitaciones. | `experiment_registry.csv`, resultados por objetivo. |
| 7. Resultados y discusion | Relacionar evidencia con objetivos | Separar resultados de interpretacion, discutir limitaciones y literatura. | Matrices de resultados y conclusiones. |
| 8. Defensa | Preparar demostracion academica | Crear guion de demo normal/anomalo/alto riesgo y preguntas del jurado. | Outline, demo script y Q&A. |

## F. Archivos creados en esta primera ejecucion

- `research/README.md`
- `research/00_control/project_status.md`
- `research/00_control/requirements_traceability.md`
- `research/00_control/academic_decisions.md`
- `research/00_control/change_log.md`
- `research/00_control/evidence_index.md`
- `research/00_control/tutor_feedback.md`

## G. Avance Modulo 1 - Anteproyecto

Fecha de avance: 2026-09-30  
Estado: DRAFT / PENDING_TUTOR_REVIEW  
Restricciones aplicadas: no se modifico codigo funcional, no se reentrenaron modelos, no se modifico Risk Engine, no se modificaron datasets y no se generaron resultados nuevos.

Archivos creados:

- `research/01_anteproyecto/tema.md`
- `research/01_anteproyecto/problema.md`
- `research/01_anteproyecto/pregunta.md`
- `research/01_anteproyecto/delimitacion.md`
- `research/01_anteproyecto/objetivos.md`
- `research/01_anteproyecto/justificacion.md`
- `research/01_anteproyecto/anteproyecto.md`

Control de calidad:

- Problema - pregunta: coherente.
- Pregunta - objetivo general: coherente.
- Objetivo general - objetivos especificos: coherente.
- Objetivos - futura metodologia: coherente de forma preliminar.
- Objetivos - futuros resultados: coherente de forma preliminar.

Puntos pendientes:

- Validacion del tutor.
- Fuentes verificables sobre remesas, digitalizacion financiera, riesgo transaccional e IA aplicada.
- Definicion final del dataset academico.
- Aprobacion de la pregunta definitiva.

## Proximo paso recomendado

Revisar con el tutor el Modulo 1 creado en `research/01_anteproyecto/anteproyecto.md`. No iniciar Modulo 2 hasta contar con aprobacion o retroalimentacion.
