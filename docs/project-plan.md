# FIDUCIA 2.0 - Planificacion tecnica del proyecto

## 1. Proposito del documento

Este documento define la planificacion tecnica inicial de **FIDUCIA**, un prototipo academico y tecnologico de una plataforma inteligente de remesas digitales hacia Guatemala.

FIDUCIA debe demostrar la integracion coherente de:

- negocio FinTech;
- simulacion de remesas;
- analitica de datos;
- inteligencia artificial aplicada a riesgo transaccional;
- dashboards ejecutivos;
- seguridad proporcional a un prototipo academico;
- documentacion trazable para defensa universitaria.

Este documento no implementa aun el sistema. Sirve como referencia principal para iniciar posteriormente la Fase 1 con criterios de aceptacion claros.

## 2. Alcance inicial

FIDUCIA sera construido como un prototipo funcional ejecutable localmente. El sistema permitira simular remesas, registrar usuarios y beneficiarios ficticios, analizar transacciones, calcular costos, generar scores de riesgo, mostrar dashboards y documentar el valor agregado de modelos de machine learning frente a un baseline basado en reglas.

### Fuera de alcance inicial

- Operaciones financieras reales.
- Custodia o transmision real de dinero.
- Integraciones bancarias productivas.
- Verificacion KYC/AML certificada.
- Uso de documentos bancarios o personales reales.
- Blockchain en la primera version funcional.
- Afirmaciones regulatorias o de cumplimiento certificadas.

## 3. Disclaimer academico obligatorio

FIDUCIA es un prototipo academico desarrollado con fines educativos y de investigacion. No constituye una entidad financiera, transmisor de dinero ni proveedor real de servicios de remesas.

Los mecanismos de scoring, deteccion de fraude, analisis de riesgo, KYC y AML incluidos en el prototipo son simulaciones academicas y no constituyen sistemas certificados de cumplimiento regulatorio.

Los datos utilizados deberan clasificarse como sinteticos, simulados o externos documentados. No se deben inventar resultados, metricas, fuentes, estadisticas ni conclusiones.

## 4. Arquitectura propuesta

La arquitectura sera modular, simple y extensible. Se prioriza reproducibilidad y mantenibilidad sobre complejidad innecesaria.

```text
Frontend Web
  |
  v
API Backend REST
  |
  +--> Motor de negocio de remesas
  |
  +--> Motor de riesgo basado en reglas
  |
  +--> Servicio de inferencia ML
  |
  +--> Motor de analitica y KPIs
  |
  v
Base de datos relacional
  |
  v
Datos sinteticos / externos documentados
```

### Componentes

**Frontend**

Aplicacion web responsive para clientes, analistas de riesgo y administradores. Debe incluir simulador, dashboards, historial, alertas, configuracion y visualizaciones.

**Backend**

API REST versionada bajo `/api/v1/`. Contendra autenticacion, autorizacion, reglas de negocio, persistencia, analitica y orquestacion de riesgo.

**Base de datos**

SQLite para el prototipo local inicial, con abstraccion mediante ORM para facilitar migracion posterior a PostgreSQL.

**Motor de riesgo**

Componente hibrido que combina reglas de negocio, probabilidad ML y opcionalmente deteccion de anomalias. Debe conservar separacion conceptual entre `rule_score`, `ml_probability`, `anomaly_score` y `final_risk_score`.

**Machine Learning**

Modulo Python separado para entrenamiento, evaluacion, versionamiento e inferencia. El primer modelo desplegable debe ser explicable y reproducible.

**Analitica**

Modulo encargado de KPIs, series historicas, dashboards, proyecciones financieras y analisis de remesas Guatemala.

## 5. Tecnologias seleccionadas

### Frontend

- **React + TypeScript**: interfaz moderna, mantenible y adecuada para dashboards.
- **Vite**: entorno ligero para prototipos y demos locales.
- **Tailwind CSS**: velocidad de construccion visual y consistencia UI.
- **Recharts**: graficas accesibles para dashboards ejecutivos y analiticos.

Decision: usar Vite en lugar de Next.js para la primera version porque FIDUCIA sera principalmente una app local demostrable, sin requerimientos iniciales de SSR, rutas server-side o despliegue complejo.

### Backend

- **Python 3.11+**
- **FastAPI**: API clara, documentacion automatica, validacion con Pydantic.
- **SQLAlchemy**: ORM con ruta natural de SQLite a PostgreSQL.
- **Alembic**: migraciones de base de datos.
- **Pydantic Settings**: configuracion centralizada.
- **PyJWT o python-jose**: autenticacion JWT.
- **Passlib + bcrypt**: hashing de contrasenas.
- **Pytest**: pruebas unitarias e integracion.

### Base de datos

- **SQLite** inicialmente para ejecucion local simple.
- **PostgreSQL** como objetivo de migracion documentado.

### Machine Learning

- **pandas, numpy, scikit-learn, joblib**.
- **matplotlib** para artefactos simples de evaluacion si se requieren.
- No usar MLflow inicialmente; el tracking se hara con JSON/CSV versionado.
- XGBoost queda como opcion futura, no dependencia inicial.

### Contenedores

- Docker Compose se preparara cuando exista una primera version integrada.
- Inicialmente no es obligatorio para ejecutar la Fase 1.

## 6. Estructura de carpetas propuesta

```text
fiducia/
|
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |   |-- components/
|   |   |-- features/
|   |   |-- hooks/
|   |   |-- lib/
|   |   |-- pages/
|   |   |-- routes/
|   |   |-- styles/
|   |   `-- types/
|   |-- public/
|   |-- package.json
|   `-- vite.config.ts
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- v1/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- repositories/
|   |   |-- security/
|   |   `-- main.py
|   |-- alembic/
|   |-- tests/
|   |-- requirements.txt
|   `-- pyproject.toml
|
|-- ml/
|   |-- datasets/
|   |-- preprocessing/
|   |-- models/
|   |-- training/
|   |-- evaluation/
|   |-- inference/
|   |-- experiments/
|   `-- notebooks/
|
|-- data/
|   |-- synthetic/
|   |-- external/
|   `-- metadata/
|
|-- notebooks/
|-- docs/
|-- scripts/
|-- tests/
|-- database/
|-- docker/
|-- README.md
|-- docker-compose.yml
`-- .env.example
```

Nota: si el repositorio se crea directamente en el directorio actual, la carpeta raiz `fiducia/` puede omitirse y sus subcarpetas pueden vivir en la raiz del proyecto.

## 7. Modelo de datos inicial

El modelo de datos debe normalizar lo suficiente para evitar duplicaciones obvias, pero mantenerse comprensible para fines academicos.

### Tabla `roles`

- `id`
- `name`: `sender`, `risk_analyst`, `admin`
- `description`
- `created_at`

### Tabla `users`

- `id`
- `role_id`
- `first_name`
- `last_name`
- `email`
- `phone`
- `country`
- `password_hash`
- `fictitious_document_id`
- `birth_date`
- `occupation`
- `is_active`
- `created_at`
- `updated_at`

### Tabla `beneficiaries`

- `id`
- `sender_id`
- `first_name`
- `last_name`
- `relationship`
- `department`
- `municipality`
- `delivery_method`
- `bank_name`
- `account_type`
- `account_last_four`
- `created_at`
- `updated_at`

### Tabla `countries`

- `id`
- `name`
- `iso_code`
- `currency_code`
- `is_origin_enabled`
- `is_destination_enabled`
- `simulated_risk_weight`

### Tabla `exchange_rates`

- `id`
- `source_currency`
- `destination_currency`
- `rate`
- `source`
- `is_simulated`
- `effective_date`
- `created_at`

### Tabla `system_parameters`

- `id`
- `key`
- `value`
- `value_type`
- `description`
- `updated_by`
- `updated_at`

Parametros iniciales:

- `commission_rate = 0.0225`
- `default_exchange_rate_usd_gtq`
- `risk_weight_rules = 0.40`
- `risk_weight_ml = 0.60`
- `risk_weight_anomaly = 0.00`
- `default_model_version`

### Tabla `transactions`

- `id`
- `transaction_id`
- `sender_id`
- `beneficiary_id`
- `origin_country`
- `destination_country`
- `amount`
- `currency`
- `exchange_rate`
- `commission_rate`
- `commission_amount`
- `total_amount`
- `destination_amount`
- `payment_method`
- `delivery_method`
- `device_id`
- `ip_address`
- `status`
- `created_at`
- `updated_at`

### Tabla `risk_scores`

- `id`
- `transaction_id`
- `rule_score`
- `ml_probability`
- `anomaly_score`
- `final_risk_score`
- `risk_level`
- `model_version`
- `explanation_summary`
- `created_at`

### Tabla `risk_rules`

- `id`
- `code`
- `name`
- `description`
- `points`
- `is_active`
- `created_at`
- `updated_at`

### Tabla `risk_alerts`

- `id`
- `transaction_id`
- `risk_score_id`
- `alert_type`
- `severity`
- `status`
- `assigned_to`
- `analyst_notes`
- `created_at`
- `resolved_at`

### Tabla `risk_rule_hits`

- `id`
- `risk_score_id`
- `rule_id`
- `points_applied`
- `evidence`

Esta tabla adicional se recomienda para explicar claramente que reglas fueron activadas.

### Tabla `audit_logs`

- `id`
- `user_id`
- `action`
- `entity`
- `entity_id`
- `metadata`
- `created_at`

### Tabla `analytics_snapshots`

- `id`
- `snapshot_date`
- `metric_name`
- `metric_value`
- `dimensions`
- `source`
- `is_simulated`
- `created_at`

### Tabla `external_dataset_metadata`

- `id`
- `dataset_name`
- `source`
- `license`
- `download_date`
- `period_covered`
- `unit_of_measure`
- `transformations`
- `limitations`
- `created_at`

Se agrega para mantener trazabilidad academica de datos externos.

## 8. Flujo principal del sistema

### Flujo de simulacion y creacion de remesa

1. El usuario inicia sesion como cliente remitente.
2. Registra o selecciona un beneficiario.
3. Ingresa pais de origen, destino Guatemala, monto, metodo de pago y metodo de entrega.
4. El backend obtiene la comision y tipo de cambio desde `system_parameters` o `exchange_rates`.
5. El motor de negocio calcula:
   - comision;
   - costo total;
   - monto estimado a recibir;
   - tiempo estimado;
   - estado inicial.
6. Si el usuario confirma, se crea la transaccion en estado `CREATED`.
7. La transaccion pasa por `VALIDATING` y `RISK_ANALYSIS`.
8. El motor de riesgo calcula `rule_score`.
9. El servicio ML calcula `ml_probability`.
10. El sistema combina senales en `final_risk_score`.
11. Se clasifica el riesgo:
   - 0-30: Bajo;
   - 31-60: Medio;
   - 61-80: Alto;
   - 81-100: Critico.
12. Si el riesgo es bajo o medio, la operacion puede pasar a `APPROVED` o `PROCESSING`.
13. Si el riesgo es alto o critico, se crea una alerta y la transaccion queda en `REVIEW_REQUIRED`.
14. El usuario ve el estado amigable y el analista puede revisar la explicacion.

## 9. Arquitectura de IA

La IA se implementara como un modulo separado dentro del repositorio y se integrara mediante una capa de inferencia invocada por el backend.

### Pipeline

```text
Dataset
  -> Exploracion
  -> Limpieza
  -> Feature engineering
  -> Train/test split
  -> Baseline basado en reglas
  -> Baseline ML con Logistic Regression
  -> Modelos candidatos
  -> Evaluacion
  -> Comparacion
  -> Seleccion
  -> Exportacion con joblib
  -> Registro de metadatos
  -> Integracion con API
```

### Features iniciales

- `transaction_amount`
- `transactions_last_24h`
- `average_transaction_amount`
- `amount_deviation`
- `beneficiaries_count`
- `new_beneficiary`
- `new_device`
- `origin_country`
- `hour_of_day`
- `day_of_week`
- `transaction_frequency`
- `previous_fraud_flag`
- `distance_from_usual_location`
- `account_age_days`

### Modelos a evaluar

- Rule-Based Risk Engine como baseline de negocio.
- Logistic Regression como baseline ML.
- Random Forest como candidato principal.
- Gradient Boosting como candidato secundario.
- Isolation Forest solo si se decide incluir deteccion no supervisada de anomalias.

### Criterio de seleccion

El modelo seleccionado no sera necesariamente el mas complejo. Se seleccionara por:

- recall;
- precision;
- F1;
- ROC-AUC;
- PR-AUC si aplica;
- matriz de confusion;
- explicabilidad;
- reproducibilidad;
- estabilidad;
- facilidad de integracion.

Accuracy no sera metrica principal por el desbalance esperado en datasets de fraude.

## 10. Arquitectura de analitica

La analitica se calculara inicialmente desde la base transaccional mediante servicios del backend.

### KPIs ejecutivos

- Total de transacciones.
- Monto total procesado.
- Ticket promedio.
- Usuarios activos.
- Comision generada.
- Transacciones de riesgo alto.
- Tasa de alertas.
- Beneficiarios registrados.

### Visualizaciones

- Transacciones por mes.
- Monto procesado por mes.
- Distribucion por pais de origen.
- Distribucion de riesgo.
- Transacciones sospechosas.
- Ticket promedio.
- Comision generada.
- Usuarios nuevos.
- Top beneficiarios.
- Horarios de mayor actividad.
- Distribucion por departamento de Guatemala.

### Proyecciones financieras

El modulo financiero usara supuestos configurables:

- usuarios;
- transacciones por usuario;
- ticket promedio;
- comision;
- crecimiento;
- costos tecnologicos;
- costos administrativos;
- marketing;
- costos operativos.

Indicadores previstos:

- ingresos;
- costos;
- flujo de caja;
- punto de equilibrio;
- ROI;
- VAN;
- TIR;
- payback.

Estos calculos deben implementarse como funciones puras para facilitar pruebas.

## 11. Estrategia de datos

### Datos sinteticos

Se generara un dataset reproducible con semilla configurable:

```bash
python scripts/generate_demo_data.py --users 500 --transactions 10000 --seed 42
```

Debe incluir:

- 500 usuarios ficticios;
- 1,000 beneficiarios;
- 10,000 transacciones;
- 12 a 24 meses de actividad;
- operaciones normales;
- montos altos;
- patrones anomalos documentados;
- diferentes paises de origen;
- horarios variados;
- multiples estados.

### Datos externos

Los datos macroeconomicos de Guatemala se guardaran separados de datos transaccionales:

```text
data/external/
data/metadata/
```

Cada dataset externo debe documentar:

- fuente;
- licencia;
- fecha de descarga;
- periodo cubierto;
- unidad de medida;
- transformaciones;
- limitaciones;
- diferencia entre el dataset y el contexto real de FIDUCIA.

### Principio de integridad

Todo dato debe clasificarse como:

- sintetico;
- simulado;
- externo documentado;
- calculado;
- pendiente.

## 12. Estrategia de baseline y evaluacion ML

### Baseline de negocio

El Rule-Based Risk Engine sera el primer baseline funcional. Permitira demostrar decisiones comprensibles, trazables y explicables aun antes de entrenar modelos.

Ejemplos de reglas:

- monto alto frente al promedio historico;
- multiples transacciones en corto tiempo;
- beneficiario nuevo;
- dispositivo nuevo;
- pais con riesgo simulado alto;
- frecuencia anormal;
- multiples beneficiarios recientes.

### Baseline ML

Logistic Regression servira como primer modelo supervisado por su explicabilidad y bajo costo computacional.

### Comparacion

La comparacion entre reglas y ML debe responder:

> Que valor adicional aporta IA frente a un sistema tradicional basado solo en reglas?

La evaluacion debe mostrar:

- metricas del baseline de reglas;
- metricas del baseline ML;
- metricas de modelos candidatos;
- analisis de falsos positivos;
- analisis de falsos negativos;
- justificacion del modelo seleccionado.

Si las metricas aun no han sido calculadas, deben aparecer como pendientes y no como resultados.

## 13. Estrategia de versionamiento del modelo

Cada modelo entrenado debe generar:

- archivo `.joblib`;
- archivo de metadatos `.json`;
- registro en `ml/experiments/experiments.jsonl` o CSV;
- version unica, por ejemplo `fraud_model_v1.0`;
- fecha de entrenamiento;
- algoritmo;
- dataset;
- features;
- parametros;
- metricas;
- semilla;
- observaciones.

Cada inferencia en la aplicacion debe registrar:

- `model_version`;
- `ml_probability`;
- fecha de inferencia;
- features principales utilizadas si aplica;
- referencia al score final.

No se deben sobrescribir silenciosamente modelos anteriores.

## 14. Seguridad y privacidad

### Controles iniciales

- Hashing de contrasenas con bcrypt.
- JWT para autenticacion.
- Roles y autorizacion por endpoint.
- Validacion de entrada con Pydantic.
- Manejo consistente de errores.
- Variables de entorno.
- Auditoria de acciones relevantes.
- Datos ficticios para usuarios y beneficiarios.

### Manejo de errores API

Formato recomendado:

```json
{
  "success": false,
  "error": {
    "code": "TRANSACTION_NOT_FOUND",
    "message": "Transaction not found"
  }
}
```

### Privacidad

No se almacenaran tarjetas reales, cuentas completas, documentos reales ni informacion financiera sensible real.

## 15. API inicial propuesta

Todos los endpoints se versionaran bajo `/api/v1/`.

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/users/me

GET  /api/v1/beneficiaries
POST /api/v1/beneficiaries
GET  /api/v1/beneficiaries/{id}

POST /api/v1/remittances/simulate
POST /api/v1/transactions
GET  /api/v1/transactions
GET  /api/v1/transactions/{id}

GET  /api/v1/risk/transactions
GET  /api/v1/risk/alerts
PATCH /api/v1/risk/alerts/{id}

GET  /api/v1/analytics/overview
GET  /api/v1/analytics/remittances
GET  /api/v1/analytics/risk

POST /api/v1/ml/predict

GET  /api/v1/config/parameters
PATCH /api/v1/config/parameters/{key}
```

## 16. Riesgos tecnicos

### Riesgo: alcance excesivo

FIDUCIA tiene muchos modulos potenciales. Mitigacion: trabajar por fases y exigir criterios de aceptacion verificables antes de avanzar.

### Riesgo: datos no representativos

Los datasets publicos de fraude financiero pueden no representar remesas guatemaltecas. Mitigacion: documentar diferencias, usar datos sinteticos con patrones conocidos y no presentar conclusiones externas como hechos del mercado real.

### Riesgo: interpretacion indebida del score

El score podria confundirse con cumplimiento AML/KYC real. Mitigacion: disclaimers visibles, documentacion etica y lenguaje de apoyo a decision academica.

### Riesgo: sobrearquitectura

Separar demasiados servicios puede complicar la demo. Mitigacion: monorepo modular, un backend FastAPI y modulo ML importable inicialmente.

### Riesgo: rendimiento con 10,000 transacciones

SQLite deberia soportar el prototipo, pero dashboards pueden requerir consultas eficientes. Mitigacion: indices, agregaciones y snapshots si se necesita.

### Riesgo: evaluacion ML debil

Sin dataset adecuado, la comparacion ML puede ser artificial. Mitigacion: documentar datos, usar baseline claro, separar resultados calculados de hipotesis y mantener reproducibilidad.

### Riesgo: seguridad incompleta

El prototipo academico no debe descuidar autenticacion y autorizacion. Mitigacion: incluir seguridad desde Fase 1 y pruebas basicas de permisos.

## 17. Supuestos iniciales

- El sistema se ejecutara localmente para demostraciones academicas.
- SQLite sera suficiente para la primera version.
- El destino inicial sera Guatemala.
- La moneda de origen inicial sera USD para la mayoria de escenarios.
- La comision inicial sera 2.25 % y estara centralizada en configuracion.
- El tipo de cambio inicial sera simulado y configurable.
- Los usuarios, beneficiarios y transacciones seran ficticios.
- El primer modelo ML puede entrenarse con datos sinteticos si no se define todavia un dataset publico.
- La prioridad es una demo defendible de 5 a 10 minutos, no una plataforma productiva.

## 18. Dudas y decisiones pendientes

1. Confirmar si el repositorio final debe crearse en la raiz actual o dentro de una carpeta `fiducia/`.
2. Confirmar idioma principal de la interfaz: espanol, ingles o bilingue.
3. Confirmar si se requiere usar Next.js por requisito academico o si Vite + React es aceptable.
4. Definir si la primera demo debe usar solamente datos sinteticos o incluir desde temprano datos externos de remesas Guatemala.
5. Definir fuente oficial preferida para datos macroeconomicos de Guatemala cuando se habilite esa fase.
6. Definir si se necesita una presentacion o memoria academica paralela al repositorio tecnico.
7. Definir si los roles de analista y administrador compartiran login inicial o cuentas seed separadas.
8. Confirmar si se desea preparar despliegue en cloud al final o mantener solo ejecucion local.

## 19. Roadmap detallado

### Rebaseline funcional aplicado

Antes de avanzar a Data, Machine Learning, Risk Engine, Analytics o fases posteriores, FIDUCIA consolida el nucleo transaccional: registro, login, perfil, beneficiarios, metodos de pago ficticios, cotizacion, comision, FX, remesas enviadas, remesas recibidas, tracking, recepcion/cobro, auditoria y pruebas.

El detalle operativo queda documentado en:

- `docs/foundation-gap-analysis.md`
- `docs/remittance-lifecycle.md`

### Fase 1 - Fundacion

Objetivo: crear la base tecnica del repositorio, backend, frontend, configuracion, base de datos y autenticacion inicial.

Archivos esperados:

- `backend/`
- `frontend/`
- `.env.example`
- `README.md`
- `docs/architecture.md`
- `docs/security.md`

Dependencias:

- Python;
- Node.js;
- SQLite;
- paquetes base backend/frontend.

Criterios de aceptacion:

- El backend FastAPI inicia localmente sin errores.
- El frontend React inicia localmente sin errores.
- Existe configuracion centralizada para comision, tipo de cambio y JWT.
- Existe modelo inicial de usuarios y roles.
- Registro y login funcionan con contrasena hasheada.
- Endpoints protegidos rechazan usuarios no autenticados.
- README contiene pasos de instalacion y ejecucion.
- Hay pruebas basicas de autenticacion.

### Fase 2 - Remesas y beneficiarios

Objetivo: implementar beneficiarios, simulador de remesas y creacion de transacciones simuladas.

Archivos esperados:

- servicios de beneficiarios;
- servicios de remesas;
- modelos de transacciones;
- pantallas de simulador, beneficiarios e historial.

Criterios de aceptacion:

- Un cliente puede registrar beneficiarios ficticios.
- El simulador calcula comision de 2.25 % desde configuracion.
- El simulador calcula costo total y monto estimado en GTQ.
- Una transaccion puede crearse desde una simulacion confirmada.
- Los estados iniciales se guardan correctamente.
- No se almacenan datos bancarios reales.
- Hay pruebas de comision, tipo de cambio y creacion de transacciones.

### Fase 3 - Datos, pipeline analitico y analitica descriptiva base

Objetivo: construir una capa analitica separada de la base operacional para datos sinteticos reproducibles, validaciones, feature engineering y analitica descriptiva inicial.

Archivos esperados:

- `scripts/generate_synthetic_data.py`
- `scripts/data_pipeline.py`
- `scripts/descriptive_analytics.py`
- `backend/app/analytics/`
- `backend/app/api/v1/endpoints/analytics.py`
- `data/synthetic/`
- `data/external/`
- `data/raw/`
- `data/processed/`
- `docs/phase3-data-plan.md`
- `docs/data-dictionary.md`
- `docs/data-sources.md`
- `docs/data-pipeline.md`

Criterios de aceptacion:

- Existe generador reproducible con `--records`, `--seed` y `--fraud-rate`.
- Se genera un dataset inicial de al menos 10,000 remesas sinteticas.
- El pipeline valida duplicados, paises, monedas, estados, fechas y calculos monetarios.
- El dataset procesado incluye features de comportamiento y variables experimentales para fases posteriores.
- La API expone endpoints `/analytics` de solo lectura para `ADMIN` y `RISK_ANALYST`.
- La interfaz contiene una vista basica de `Analitica` integrada con el estilo de FIDUCIA.
- No se entrena Machine Learning ni se activa un Risk Engine definitivo.
- Las funcionalidades de Fase 1 y Fase 2 continuan funcionando.

### Fase 4 - Machine Learning e inteligencia de riesgo

Objetivo: entrenar, evaluar, versionar e integrar un modelo supervisado para estimar `ml_probability` como senal de apoyo al analisis de riesgo.

Archivos esperados:

- `ml/training/`
- `ml/evaluation/`
- `ml/inference/`
- `ml/artifacts/fraud_model.joblib`
- `backend/app/services/ml_risk.py`
- `backend/app/api/v1/endpoints/risk.py`
- `docs/phase4-ml-plan.md`
- `docs/ml-methodology.md`
- `docs/ml-evaluation.md`
- `docs/ml-model-card.md`

Criterios de aceptacion:

- Existe auditoria de leakage.
- Existe EDA documentado.
- Existe baseline.
- Logistic Regression, Random Forest y Gradient Boosting estan evaluados.
- Existe comparacion objetiva de metricas.
- Modelo final versionado como `fraud-model-v1`.
- API protegida `/risk/ml/*` disponible para `ADMIN` y `RISK_ANALYST`.
- Vista `Inteligencia de riesgo` integrada al frontend.
- No se implementa Risk Engine definitivo ni bloqueo automatico.

### Fase 5 - Machine Learning

Objetivo: crear pipeline reproducible de entrenamiento, evaluacion, versionamiento e inferencia.

Archivos esperados:

- `ml/training/train_fraud_model.py`
- `ml/evaluation/`
- `ml/inference/`
- `ml/experiments/`
- notebooks iniciales.

Criterios de aceptacion:

- Existe dataset documentado, aunque sea sintetico.
- Se entrena Logistic Regression como baseline ML.
- Se evalua al menos un modelo candidato adicional.
- Se calculan precision, recall, F1, ROC-AUC y matriz de confusion.
- Se exporta un modelo con joblib.
- Se genera metadata con version, features, dataset, metrica y semilla.
- La API puede obtener `ml_probability`.
- No se reportan metricas no calculadas.

### Fase 6 - Integracion de riesgo hibrido y alertas

Objetivo: combinar reglas y ML para score final, generar alertas y permitir revision por analista.

Archivos esperados:

- endpoints de riesgo;
- dashboard de riesgo;
- alertas;
- vista de detalle de transaccion con explicacion.

Criterios de aceptacion:

- `final_risk_score` combina pesos configurables.
- `model_version` se registra por inferencia.
- Transacciones de riesgo alto o critico generan alertas.
- El analista puede filtrar alertas por riesgo, fecha, pais, usuario y estado.
- El analista puede agregar observaciones.
- La explicacion separa reglas, ML y score final.
- Hay pruebas de combinacion de score, alertas y permisos.

### Fase 7 - Analitica ejecutiva

Objetivo: construir dashboards de negocio y KPIs.

Nota de rebaseline: la Fase 3 ya implementa analitica descriptiva base, endpoints protegidos `/analytics` y una vista ligera de Analitica. La Fase 7 queda reservada para BI avanzado, filtros ejecutivos, cohortes, segmentacion y tableros mas completos.

Archivos esperados:

- servicios de analytics;
- endpoints `/analytics`;
- dashboard administrador;
- dashboard analitico.

Criterios de aceptacion:

- Se muestran KPIs principales.
- Las graficas cargan desde datos reales del prototipo.
- Los ingresos se calculan como monto transaccionado por comision.
- El ticket promedio se calcula correctamente.
- Los datos sinteticos se identifican como tales.
- Hay pruebas para calculos principales.

### Fase 8 - Proyecciones financieras

Objetivo: implementar escenarios financiero-operativos configurables.

Archivos esperados:

- modulo de proyecciones;
- funciones financieras;
- pantalla de escenarios.

Criterios de aceptacion:

- Existen escenarios conservador, base y optimista.
- Los supuestos son editables o centralizados.
- Se calculan ingresos, costos, flujo de caja, punto de equilibrio, ROI, VAN, TIR y payback cuando existan datos suficientes.
- Los resultados se identifican como proyecciones basadas en supuestos.
- Hay pruebas de formulas financieras.

### Fase 9 - Remesas Guatemala y forecasting

Objetivo: importar datos externos de remesas Guatemala y crear analisis historico con proyeccion simple.

Archivos esperados:

- importador CSV;
- metadata de fuente;
- dashboard Remesas Guatemala;
- modulo de forecasting simple.

Criterios de aceptacion:

- Se puede importar CSV macroeconomico.
- La fuente, periodo y transformaciones quedan documentadas.
- El dashboard muestra evolucion, crecimiento anual, variacion mensual y promedio movil.
- La proyeccion usa un baseline sencillo.
- Las limitaciones del pronostico estan documentadas.
- No se presenta ninguna proyeccion como certeza.

### Fase 10 - Experiencia, Fidu y defensa

Objetivo: pulir UX/UI, preparar asistente estructurado Fidu y consolidar material de defensa.

Archivos esperados:

- asistente Fidu con respuestas estructuradas;
- mejoras responsive;
- capturas o guion demo;
- documentacion academica final.

Criterios de aceptacion:

- La demo de 5 a 10 minutos puede ejecutarse de punta a punta.
- Fidu responde preguntas frecuentes sin asesoria financiera personalizada.
- Existen casos demo normal y anomalos.
- La documentacion explica el valor de IA frente a reglas.
- Los disclaimers academicos son visibles donde corresponde.
- La interfaz es consistente, profesional y responsive.

## Fase 5 - Risk Engine

Estado: completada.

Se implementa `risk-engine-v1.1` combinando `rules-v1`, `fraud-model-v1` y `anomaly-model-v1`. Los pesos `30/50/20` se documentan como baseline heuristico inicial. Las bandas quedan como `LOW < 25`, `MEDIUM 25-39.99`, `HIGH >= 40`. Incluye persistencia de evaluaciones, explicaciones deterministicas, cola de revision humana, dashboard de riesgo y estudio de ablacion. El motor no bloquea remesas automaticamente y mantiene human-in-the-loop.

## Fase 6 - Forecasting y Analitica Predictiva

Estado: completada.

Se implementa `remittance-forecast-v1` para pronostico semanal experimental de `transaction_count` y `transaction_amount_usd`. La decision metodologica del dataset es `CONDITIONAL` por tratarse de datos sinteticos con 18 meses de historia. El modulo usa split cronologico, walk-forward validation, baselines, comparacion de modelos, artefactos versionados, API protegida y frontend `Analitica predictiva`.

## Fase 7 - Business Intelligence

Estado: implementada sobre Fases 1-6 en rama `phase7-business-intelligence`.

Incluye catalogo central de KPIs, formulas documentadas, comparacion temporal, revenue con comisiones historicas, multimoneda en USD equivalente, corredores, clientes agregados, operaciones, riesgo agregado, forecast ejecutivo, insights deterministricos, export CSV y frontend `Inteligencia de negocio`. No crea modelos nuevos, no recalcula riesgo y no reentrena forecasting.

## 20. Criterios globales de calidad

Para considerar FIDUCIA listo como prototipo academico:

- La simulacion de remesa funciona de punta a punta.
- La comision configurable se aplica correctamente.
- El riesgo se calcula con trazabilidad.
- El modelo ML registra version e inferencia.
- Los dashboards usan datos del sistema.
- Los datos sinteticos y externos estan diferenciados.
- La seguridad basica esta implementada.
- Las pruebas relevantes pasan.
- La documentacion explica arquitectura, datos, IA, analitica, seguridad y limitaciones.
- La demo permite responder que valor aporta IA frente a reglas.

## 21. Decision tecnica inicial recomendada

La primera implementacion deberia comenzar por una arquitectura monorepo con:

- backend FastAPI;
- frontend React + TypeScript + Vite;
- SQLite;
- SQLAlchemy;
- modulo ML Python dentro del mismo repositorio;
- datos sinteticos reproducibles;
- configuracion centralizada.

Esta decision reduce friccion para una defensa academica local, mantiene separacion modular suficiente y permite evolucionar posteriormente hacia PostgreSQL, servicios separados, integraciones externas o despliegue cloud si el proyecto lo requiere.

## 22. Siguiente paso

Antes de iniciar la Fase 1 se requiere aprobacion del propietario del proyecto sobre:

- ubicacion final del repositorio;
- stack frontend definitivo;
- idioma de interfaz;
- uso inicial de datos sinteticos;
- prioridad de la primera demo.

Con esa confirmacion, la Fase 1 puede comenzar con la creacion del repositorio tecnico, backend, frontend, autenticacion y configuracion base.
