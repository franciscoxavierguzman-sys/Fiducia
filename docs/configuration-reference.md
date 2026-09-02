# Referencia de configuracion

FIDUCIA usa variables de entorno con placeholders en `.env.example`. No se deben versionar secretos reales.

| Variable | Proposito | Default local | Sensible |
|---|---|---|---|
| `APP_NAME` | Nombre del servicio | `FIDUCIA` | No |
| `ENVIRONMENT` | Ambiente de ejecucion | `development` | No |
| `API_V1_PREFIX` | Prefijo API | `/api/v1` | No |
| `DATABASE_URL` | Conexion DB | SQLite local | Puede serlo |
| `SECRET_KEY` | Firma JWT | Placeholder | Si |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiracion JWT | `60` | No |
| `CORS_ORIGINS` | Origenes frontend permitidos | localhost/127.0.0.1 para Vite local | No |
| `COMMISSION_RATE` | Comision base | `0.0225` | No |
| `DEFAULT_EXCHANGE_RATE_USD_GTQ` | Fallback FX | `7.80` | No |
| `MINIMUM_REMITTANCE_AMOUNT` | Monto minimo | `10` | No |
| `MAXIMUM_REMITTANCE_AMOUNT` | Monto maximo | `5000` | No |
| `ASSISTANT_PROVIDER` | Proveedor opcional | deterministic | No |
| `ASSISTANT_MODEL` | Modelo externo opcional | Placeholder | No |
| `ASSISTANT_API_KEY` | Llave proveedor externo | No incluida | Si |
| `VITE_API_BASE_URL` | API del frontend | localhost | No |

## CORS

El desarrollo local permite explicitamente:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

Tambien se conservan `5174` para el caso en que Vite elija puerto alterno. No se usa comodin global con credenciales. `BACKEND_CORS_ORIGINS` se acepta como nombre legacy, pero `CORS_ORIGINS` es la variable recomendada.

## Puertos

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:5173` o puerto alterno elegido por Vite.

## Model paths

Los artefactos se cargan desde `ml/artifacts`. Fase 10 no modifica ni reentrena artefactos.

## Blockchain

`local-blockchain-v1` mantiene dificultad local `2`. No se conecta a red publica.
