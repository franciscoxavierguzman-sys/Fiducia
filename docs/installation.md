# Instalacion local

## Requisitos

- Windows 10/11.
- Python 3.11+.
- Node.js compatible con Vite.
- PowerShell o CMD.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Configuracion

Copiar `.env.example` a `.env` para uso local y cambiar `SECRET_KEY`. No subir `.env` a Git.

## Validacion

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe ..\scripts\final_validation.py
.\.venv\Scripts\python.exe ..\scripts\run_final_e2e.py
```

```powershell
cd frontend
npm run build
```
