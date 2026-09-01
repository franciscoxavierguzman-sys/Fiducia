@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "PYTHON_BUNDLED=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

echo.
echo ==========================================
echo   FIDUCIA - Inicio local del prototipo
echo ==========================================
echo.

cd /d "%ROOT%"

if not exist ".env" (
  if exist ".env.example" (
    echo Creando .env desde .env.example...
    copy ".env.example" ".env" >nul
  ) else (
    echo ERROR: No existe .env ni .env.example.
    pause
    exit /b 1
  )
)

if not exist "%BACKEND%" (
  echo ERROR: No existe la carpeta backend.
  pause
  exit /b 1
)

if not exist "%FRONTEND%" (
  echo ERROR: No existe la carpeta frontend.
  pause
  exit /b 1
)

if exist "%BACKEND%\.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%BACKEND%\.venv\Scripts\python.exe"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_EXE=python"
  ) else if exist "%PYTHON_BUNDLED%" (
    set "PYTHON_EXE=%PYTHON_BUNDLED%"
  ) else (
    echo ERROR: No se encontro Python. Instala Python o ejecuta desde Codex con el runtime disponible.
    pause
    exit /b 1
  )

  echo Creando entorno virtual del backend...
  cd /d "%BACKEND%"
  "%PYTHON_EXE%" -m venv .venv
  if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual del backend.
    pause
    exit /b 1
  )
  set "PYTHON_EXE=%BACKEND%\.venv\Scripts\python.exe"
)

cd /d "%BACKEND%"
"%PYTHON_EXE%" -c "import fastapi, sqlalchemy, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Instalando dependencias del backend...
  "%PYTHON_EXE%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias del backend.
    pause
    exit /b 1
  )
)

cd /d "%FRONTEND%"
where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: No se encontro npm. Instala Node.js antes de iniciar el frontend.
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo Instalando dependencias del frontend...
  call npm install
  if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias del frontend.
    pause
    exit /b 1
  )
)

echo.
echo Iniciando backend en http://127.0.0.1:8000 ...
call :free_port 8000
call :free_port 5173
call :free_port 5174
start "FIDUCIA Backend" /D "%BACKEND%" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Iniciando frontend con Vite ...
start "FIDUCIA Frontend" /D "%FRONTEND%" cmd /k "npm run dev"

echo.
echo Listo. Se abrieron dos ventanas:
echo   - Backend:  http://127.0.0.1:8000/health
echo   - Frontend: revisa la URL que indique Vite, normalmente http://127.0.0.1:5173/
echo.
echo Si Vite usa 5174, el backend ya esta configurado para permitirlo.
echo Para detener FIDUCIA, cierra las dos ventanas o presiona Ctrl+C en cada una.
echo.
pause
exit /b 0

:free_port
set "PORT=%~1"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
  if not "%%P"=="0" (
    echo Cerrando proceso previo en puerto %PORT% ^(PID %%P^)...
    taskkill /PID %%P /F >nul 2>nul
  )
)
exit /b 0
