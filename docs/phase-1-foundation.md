# Fase 1 - Fundacion

## Objetivo

Crear la base tecnica de FIDUCIA con backend, frontend, configuracion, base de datos, autenticacion, roles y gestion basica de usuarios.

## Implementado

- Estructura raiz del repositorio sin carpeta `fiducia/` adicional.
- Backend FastAPI con prefijo `/api/v1`.
- Configuracion centralizada con variables de entorno.
- SQLAlchemy con SQLite y posibilidad futura de PostgreSQL.
- Modelos iniciales `roles` y `users`.
- Seed automatico de roles base.
- Registro de usuarios.
- Login con JWT.
- Endpoint protegido `/api/v1/users/me`.
- Frontend React/Vite/Tailwind con interfaz inicial en espanol.
- Formulario de login conectado a `POST /api/v1/auth/login`.
- Validacion de sesion frontend mediante `GET /api/v1/users/me`.
- Pantalla placeholder autenticada y logout basico.
- Carpetas base para ML, datos, notebooks, scripts, database y docker.

## No implementado en esta fase

- Beneficiarios.
- Simulacion de remesas.
- Transacciones.
- Risk Engine.
- Modelos de Machine Learning.
- Dashboards analiticos completos.

## Criterios de aceptacion

- Backend inicia localmente: validado con `uvicorn app.main:app --host 127.0.0.1 --port 8000`.
- Frontend inicia localmente: validado con `npm run dev`; Vite uso `http://127.0.0.1:5174/` porque `5173` estaba ocupado.
- La base de datos se crea mediante SQLAlchemy: validado con `database/fiducia.db`.
- Registro y login funcionan: validado contra API local viva.
- Endpoint protegido rechaza usuarios sin token: cubierto por pruebas automatizadas.
- El formulario frontend consume el endpoint real de login.
- El frontend maneja carga, credenciales incorrectas, errores de conexion, sesion activa y logout.
- Pruebas de autenticacion existen y pasan.
- Documentacion minima actualizada.

## Decisiones adicionales

- No se agrego Alembic todavia porque Fase 1 usa `Base.metadata.create_all` para acelerar la demo local. Alembic sigue recomendado antes de ampliar el modelo de datos en fases posteriores.
- Se reemplazo `python-jose[cryptography]` por `PyJWT` para evitar dependencias criptograficas innecesarias en la fundacion. La autenticacion sigue usando JWT firmado con HS256.
- Se fijo `bcrypt==4.0.1` por compatibilidad con `passlib==1.7.4`.
- Se configuro SQLite en memoria con `StaticPool` para pruebas reproducibles.
- El token JWT se guarda en `localStorage` como mecanismo simple y apropiado para este prototipo local. En una version productiva se deberia reevaluar hacia cookies `HttpOnly`, `Secure`, politica CSRF y endurecimiento contra XSS.

## Validaciones ejecutadas

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

Resultado:

```text
6 passed in 5.98s
```

```bash
cd frontend
npm run build
```

Resultado:

```text
✓ built
```

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
```

Resultado:

```text
status: ok
service: FIDUCIA
```

Tambien se valido manualmente el flujo API:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`

## Ajuste de cierre: login frontend

Se conecto el formulario de login existente con el backend real.

Validaciones realizadas:

| Escenario | Resultado |
| --- | --- |
| Login correcto | Recibe token y valida sesion con `/users/me` |
| Contrasena incorrecta | API responde `401` y el frontend muestra mensaje amigable |
| Usuario inexistente | API responde `401` y el frontend muestra mensaje amigable |
| Backend no disponible | El frontend captura error de conexion y muestra mensaje |
| Endpoint protegido sin token | API responde `401` |
| Endpoint protegido con token valido | API responde datos del usuario |
| Logout | El frontend elimina token local y regresa al login |

Resultado de validacion viva:

```text
LoginTokenReceived: True
WrongPasswordStatus: 401
UnknownUserStatus: 401
NoTokenStatus: 401
BackendUnavailable: CONNECTION_ERROR
```

## Ejecucion local verificada

Backend:

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Si `5173` esta ocupado, Vite seleccionara el siguiente puerto disponible.
