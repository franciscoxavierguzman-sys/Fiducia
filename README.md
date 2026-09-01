# FIDUCIA 2.0

FIDUCIA es un prototipo tecnologico de una plataforma inteligente de remesas digitales hacia Guatemala. Esta primera entrega implementa la **Fase 1 - Fundacion**: estructura base, backend FastAPI, frontend React, configuracion, base de datos, autenticacion, roles y gestion basica de usuarios.

La **Fase 2 - Remesas** agrega beneficiarios, cotizacion de remesas bidireccionales, metodos de pago ficticios, creacion de remesas, remesas enviadas, remesas recibidas, tracking, detalle y recepcion/cobro dentro del prototipo.

La **Fase 3 - Datos** agrega generacion reproducible de datos sinteticos, pipeline analitico, validaciones automaticas, dataset procesado, analitica descriptiva, endpoints de lectura para perfiles autorizados y una vista basica de `Analitica`.

La **Fase 4 - Machine Learning** agrega entrenamiento reproducible de modelos supervisados, comparacion contra baseline, versionado de artefactos, servicio de inferencia, API protegida y vista `Inteligencia de riesgo`.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, SQLite.
- Frontend: React, TypeScript, Vite, Tailwind CSS.
- Pruebas: Pytest para backend y build TypeScript/Vite para frontend.

## Ejecucion local

### Inicio rapido en Windows

Desde la raiz del proyecto ejecuta:

```powershell
.\start-fiducia.bat
```

El script prepara `.env` si falta, valida dependencias basicas y abre dos ventanas: backend FastAPI y frontend Vite.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example ..\.env
uvicorn app.main:app --reload
```

Si `python` no esta en PATH dentro de Codex Desktop, se puede crear el entorno con el runtime bundled:

```powershell
& 'C:\Users\Javier Guzman\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv
```

API local:

```text
http://127.0.0.1:8000
```

Documentacion OpenAPI:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Aplicacion local:

```text
http://127.0.0.1:5173
```

## Pruebas

```bash
cd backend
pytest
```

Pipeline de datos:

```powershell
.\backend\.venv\Scripts\python.exe scripts\data_pipeline.py --records 10000 --seed 42
.\backend\.venv\Scripts\python.exe scripts\descriptive_analytics.py
```

Pipeline ML:

```powershell
.\backend\.venv\Scripts\python.exe scripts\run_ml_eda.py
.\backend\.venv\Scripts\python.exe scripts\train_fraud_model.py --seed 42
.\backend\.venv\Scripts\python.exe scripts\evaluate_fraud_model.py
```

En Windows tambien puedes ejecutar:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Probar registro y login desde la interfaz

1. Abre el frontend.
2. Usa `Crear cuenta`.
3. Completa datos personales, tipo de documento, No. de documento, fecha de nacimiento, contrasena y confirmacion.
4. Abre los terminos y condiciones desde el enlace del formulario, marca la verificacion humana y acepta los terminos.
5. Vuelve al login.
6. Inicia sesion con el correo y contrasena creados.

## Probar una remesa enviada

1. Inicia sesion.
2. Abre `Metodos de pago`.
3. Agrega una tarjeta, cuenta bancaria o billetera con datos de prueba.
4. Para cuenta bancaria selecciona un banco de Guatemala, tipo de cuenta y numero completo.
5. Para tarjeta selecciona Visa, Mastercard o American Express, ingresa numero completo, vencimiento y CVV.
6. Selecciona moneda en dolares o quetzales.
7. Abre `Beneficiarios`.
8. Crea un beneficiario con datos de prueba.
9. Abre `Enviar remesa`.
10. Cotiza el envio. Si el destino es Guatemala y envias desde Estados Unidos, FIDUCIA usa el tipo de cambio vigente publicado por Banguat cuando esta disponible. Puedes pagar con un metodo en USD o en GTQ; si pagas en GTQ, el total a debitar se convierte a quetzales.
11. Confirma la remesa.
12. Abre `Remesas enviadas`.
13. Revisa el detalle, imprime el comprobante o usa `Rastrear remesa`.

## Modificar datos de usuario

Despues de iniciar sesion abre `Mi perfil`. Desde esa pantalla puedes modificar nombre, apellido, correo, telefono, pais, documento, fecha de nacimiento y ocupacion. Si cambias el correo, la API valida que no exista otro usuario con el mismo correo.

La comision inicial es `2.25 %` y los tipos de cambio iniciales son simulados. Guatemala debe participar como origen o destino del corredor.

## Analitica Fase 3

Los usuarios con rol `ADMIN` o `RISK_ANALYST` pueden abrir `Analitica` en el frontend. La vista consume endpoints protegidos del backend y muestra KPIs descriptivos de la base operacional: total de remesas, volumen equivalente USD, comisiones, ticket promedio, corredor principal, evolucion temporal, estados, monedas y metodos.

Los datos de investigacion se generan aparte:

- `data/synthetic/remittances_synthetic.csv`
- `data/processed/remittances_analytics.csv`
- `data/processed/validation_report.json`
- `data/processed/descriptive_summary.json`

## Inteligencia de riesgo Fase 4

Los usuarios `ADMIN` y `RISK_ANALYST` pueden abrir `Inteligencia de riesgo`. La vista muestra modelo activo, version, precision, recall, PR-AUC, threshold, matriz de confusion, comparacion de modelos y variables relevantes.

Artefactos ML:

- `ml/artifacts/fraud_model.joblib`
- `ml/artifacts/model_metadata.json`
- `ml/artifacts/model_metrics.json`
- `reports/ml/eda_summary.json`
- `reports/ml/model_comparison.json`

Endpoints protegidos:

```text
GET  /api/v1/risk/ml/model-info
GET  /api/v1/risk/ml/metrics
POST /api/v1/risk/ml/predict
```

## Probar recepcion entre dos usuarios

1. Registra dos usuarios ficticios: remitente y beneficiario.
2. Inicia sesion como remitente.
3. Crea un beneficiario usando el correo del usuario beneficiario.
4. Envia una remesa a ese beneficiario.
5. Cierra sesion.
6. Inicia sesion como beneficiario.
7. Abre `Remesas recibidas`.
8. Abre el detalle de la remesa disponible.
9. Usa `Recibir remesa`, `Cobrar remesa` o `Confirmar recepcion`, segun el metodo.
10. Verifica que el estado cambie a `COMPLETED`.

Si el beneficiario fue creado antes de que existiera su cuenta FIDUCIA, basta con que el usuario receptor se registre o inicie sesion usando exactamente ese correo. La plataforma vincula automaticamente las remesas pendientes por correo.

```bash
cd frontend
npm run build
```

## Disclaimer

FIDUCIA es un prototipo tecnologico desarrollado con fines educativos y de investigacion. No constituye una entidad financiera ni un servicio real de remesas.

Los mecanismos de scoring, deteccion de fraude, analisis de riesgo, KYC y AML previstos no constituyen sistemas certificados de cumplimiento regulatorio.

## Risk Engine Fase 5

`risk-engine-v1.1` combina reglas, ML y deteccion de anomalias para apoyar revision interna. No bloquea ni rechaza remesas automaticamente.

Configuracion:

- Pesos: Rules 30%, ML 50%, Anomaly 20% como baseline heuristico inicial.
- Bandas: LOW < 25, MEDIUM 25 a < 40, HIGH >= 40.
- HIGH significa senales elevadas que requieren revision humana, no fraude confirmado.

Comandos:

```powershell
.\backend\.venv\Scripts\python.exe scripts\train_anomaly_model.py --seed 42
.\backend\.venv\Scripts\python.exe scripts\evaluate_risk_engine.py
cd backend
.\.venv\Scripts\python.exe -m pytest
cd ..\frontend
npm run build
```

Usuarios `ADMIN` y `RISK_ANALYST` pueden abrir `Inteligencia de riesgo` y `Revision de riesgo`. El cliente conserva su flujo normal.

## Forecasting Fase 6

`remittance-forecast-v1` agrega analitica predictiva semanal sobre datos sinteticos agregados. Forecasting esta separado del Risk Engine y no modifica decisiones de riesgo.

Comandos:

```powershell
.\backend\.venv\Scripts\python.exe scripts\prepare_forecasting_data.py
.\backend\.venv\Scripts\python.exe scripts\audit_forecasting_data.py
.\backend\.venv\Scripts\python.exe scripts\train_forecast_models.py --seed 42
.\backend\.venv\Scripts\python.exe scripts\evaluate_forecast_models.py
.\backend\.venv\Scripts\python.exe scripts\generate_forecasts.py --target transaction_count --horizon 8
```

La vista `Analitica predictiva` esta disponible para `ADMIN` y `RISK_ANALYST`.

## Business Intelligence Fase 7

La vista `Inteligencia de negocio` esta disponible para `ADMIN` y `RISK_ANALYST`. Integra KPIs ejecutivos, tendencias, revenue, corredores, clientes agregados, operaciones, riesgo agregado, forecast resumido e insights deterministricos.

Endpoints utiles:

```text
GET /api/v1/bi/overview
GET /api/v1/bi/corridors
GET /api/v1/bi/executive-summary
GET /api/v1/bi/exports/kpis.csv
GET /api/v1/bi/exports/corridors.csv
```
