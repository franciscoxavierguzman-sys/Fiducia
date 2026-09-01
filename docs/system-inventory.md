# Inventario final del sistema

| Modulo | Proposito | Archivos principales | Dependencias | Servicio owner | Criticidad |
|---|---|---|---|---|---|
| Frontend | Experiencia web integrada | `frontend/src/main.tsx`, `frontend/src/styles.css` | React, Vite, API v1 | Frontend app | Alta |
| Backend | API y orquestacion | `backend/app/main.py`, `backend/app/api/v1/router.py` | FastAPI, SQLAlchemy | FastAPI | Alta |
| Database | Persistencia operacional local | `database/fiducia.db`, `backend/app/models/*` | SQLite | SQLAlchemy | Alta |
| Authentication | Registro, login y JWT | `auth.py`, `tokens.py`, `passwords.py` | PyJWT, passlib | Auth API | Alta |
| Remittances | Cotizacion, envio y recepcion | `transactions.py`, `remittances.py` | Auth, DB, risk, blockchain | Transactions API | Alta |
| Beneficiaries | Beneficiarios propios | `beneficiaries.py`, `repositories/beneficiaries.py` | Auth, DB | Beneficiaries API | Alta |
| Funding sources | Metodos de pago ficticios | `funding_sources.py`, `repositories/funding_sources.py` | Auth, DB | Funding API | Media |
| Risk | Evaluacion y revision humana | `risk_engine.py`, `risk/*` | ML, rules, anomaly, DB | Risk API | Alta |
| ML | Probabilidad de fraude | `ml_risk.py`, `ml/artifacts/*` | joblib, pandas | ML service | Alta |
| Anomaly | Score complementario | `risk/anomaly.py`, `anomaly_model.joblib` | joblib | Risk service | Media |
| Forecast | Analitica predictiva | `forecasting.py`, `ml/artifacts/forecasting/*` | pandas, joblib | Forecast API | Media |
| BI | KPIs ejecutivos | `bi/*`, `business_intelligence.py` | DB, analytics | BI API | Alta |
| Blockchain | Evidencia local verificable | `blockchain/*`, `services/blockchain.py` | DB, SHA-256 | Blockchain API | Alta |
| Assistant | Consultas read-only con permisos | `assistant/*`, `endpoints/assistant.py` | Servicios internos | Assistant API | Media |
| Audit | Trazabilidad de acciones | `audit.py`, `models/audit_log.py` | DB | Audit service | Alta |
| Scripts | Entrenamiento, validacion y demo | `scripts/*.py` | Python local | CLI | Media |
| Tests | Regresion automatizada | `backend/tests/*` | pytest | Test suite | Alta |
| Artifacts | Modelos y metadata | `ml/artifacts/*` | Servicios ML/risk/forecast | Archivos locales | Alta |
| Reports | Evidencia metodologica | `reports/*` | Scripts | Reportes | Media |
