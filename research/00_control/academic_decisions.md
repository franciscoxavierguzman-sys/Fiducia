# Registro de decisiones academicas

Fecha de creacion: 2026-09-30  
Regla: no marcar APPROVED sin confirmacion explicita del estudiante de que el tutor lo aprobo.

## DEC-001

Fecha: 2026-09-30  
Decision: Tratar FIDUCIA como prototipo tecnologico y experimental para investigar identificacion de riesgo transaccional en remesas digitales.  
Motivo: El repositorio ya contiene flujo de remesas, Risk Engine, ML, analitica y documentacion tecnica reutilizable.  
Origen: Prompt maestro del usuario.  
Impacto: La investigacion queda como eje; funcionalidades no relacionadas pasan a ser complementarias.  
Estado: PENDING_TUTOR_REVIEW.

## DEC-002

Fecha: 2026-09-30  
Decision: Mantener la pregunta, titulo y objetivos como propuestas, no como aprobados.  
Motivo: El prompt indica que estan pendientes de aprobacion academica.  
Origen: Prompt maestro del usuario.  
Impacto: Todos los documentos academicos deben marcar estos elementos como PROPOSED o PENDING_TUTOR_REVIEW.  
Estado: PENDING_TUTOR_REVIEW.

## DEC-003

Fecha: 2026-09-30  
Decision: No modificar modelos, Risk Engine, base de datos, frontend ni funcionalidad durante la primera ejecucion.  
Motivo: La primera ejecucion exige auditoria completa y creacion exclusiva de archivos de control academico.  
Origen: Prompt maestro del usuario.  
Impacto: Se crean solo archivos bajo `research/` y no se altera logica funcional.  
Estado: PENDING_TUTOR_REVIEW.

## DEC-004

Fecha: 2026-09-30  
Decision: Considerar datos sinteticos como evidencia tecnica, no como evidencia empirica representativa de Guatemala.  
Motivo: El repositorio documenta generacion sintetica y no contiene evidencia de datasets reales de remesas guatemaltecas.  
Origen: Auditoria de `data/`, `docs/data-sources.md` y `docs/ml-evaluation.md`.  
Impacto: Cualquier analisis debe declarar limitaciones de representatividad.  
Estado: PROPOSED.

## DEC-005

Fecha: 2026-09-30  
Decision: Priorizar Recall, PR-AUC, F1 y matriz de confusion sobre Accuracy como evidencia del problema de clase desbalanceada.  
Motivo: El dataset sintetico tiene baja tasa positiva y la documentacion existente ya evita Accuracy como unica metrica.  
Origen: Auditoria de `docs/ml-evaluation.md` y `reports/ml/model_comparison.json`.  
Impacto: La justificacion metodologica debe explicar desbalance, falsos negativos y falsos positivos.  
Estado: PROPOSED / PENDING_METHODOLOGY_VALIDATION.

## DEC-006

Fecha: 2026-09-30  
Decision: Mantener blockchain, forecasting, asistente y marketplace como componentes complementarios.  
Motivo: No responden directamente al eje central provisional de identificacion de riesgo transaccional mediante IA y analitica.  
Origen: Auditoria de arquitectura y prompt maestro.  
Impacto: Pueden apoyar demostracion o contexto, pero no deben convertirse en objetivos principales sin aprobacion.  
Estado: PROPOSED.

## DEC-007

Fecha: 2026-09-30  
Decision: Iniciar exclusivamente el Modulo 1 - Planteamiento y formulacion del anteproyecto.  
Motivo: El usuario autorizo continuar con Modulo 1 y prohibio avanzar al Modulo 2 o modificar funcionalidad.  
Origen: Prompt de continuidad del usuario.  
Impacto: Se crean documentos bajo `research/01_anteproyecto/` y se actualizan controles academicos sin tocar codigo funcional, modelos, Risk Engine ni datasets.  
Estado: PENDING_TUTOR_REVIEW.

## DEC-008

Fecha: 2026-09-30  
Decision: Mantener el titulo original como propuesta y registrar una alternativa mas cautelosa sin sustituirlo automaticamente.  
Motivo: El prompt solicita evaluar criticamente el titulo y presentar alternativas si aplica.  
Origen: Revision academica del Modulo 1.  
Impacto: `tema.md` y `anteproyecto.md` contienen Version A y alternativa para tutor.  
Estado: PENDING_TUTOR_REVIEW.

## DEC-009

Fecha: 2026-09-30  
Decision: Formular la unidad de analisis como transacciones financieras digitales utilizadas para entrenamiento, validacion y evaluacion del modelo de riesgo.  
Motivo: La investigacion no estudia directamente personas, sino registros transaccionales y desempeno analitico.  
Origen: Prompt de continuidad del usuario.  
Impacto: Evita declarar poblacion humana sin diseno metodologico que lo justifique.  
Estado: PROPOSED / PENDING_TUTOR_REVIEW.

## DEC-010

Fecha: 2026-09-30  
Decision: Usar `[CITA VERIFICABLE REQUERIDA]` para afirmaciones externas que aun no cuentan con fuente validada.  
Motivo: El usuario prohibio inventar cifras, autores, DOI, URLs o referencias.  
Origen: Prompt de continuidad del usuario.  
Impacto: El Modulo 1 queda listo para posterior investigacion documental sin introducir fuentes no verificadas.  
Estado: COMPLETED.
