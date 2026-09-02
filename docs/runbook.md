# Runbook

## Backend no inicia

Verificar entorno virtual, dependencias y puerto 8000. Si el puerto esta ocupado, detener el proceso anterior o usar otro puerto y actualizar `VITE_API_BASE_URL`.

## Frontend no conecta

Confirmar que backend responda en `/health` y que `VITE_API_BASE_URL` apunte a `/api/v1`.

## SQLite locked

Cerrar procesos duplicados del backend. Para backup, copiar `database/fiducia.db` solo con backend detenido.

## Modelo no disponible

Ejecutar `python scripts/final_validation.py` y revisar `ml/artifacts`. No reentrenar durante Fase 10.

## Provider del asistente no disponible

El asistente cae al proveedor deterministico. Revisar variables `ASSISTANT_PROVIDER` y `ASSISTANT_API_KEY` si se prueba proveedor externo.

## Blockchain validation falla

Usar la demo aislada de tampering solo fuera de la DB principal. Si falla en datos reales de demo, revisar eventos de auditoria y hashes.

## Remesa sin evidencia blockchain

Si una remesa existente devuelve `NOT_FOUND` en verificacion blockchain, revisar primero que la tabla `blockchain_blocks` tenga bloques de evidencia. Para datos demo creados antes de activar la capa blockchain, ejecutar desde la raiz del proyecto:

```powershell
.\backend\.venv\Scripts\python.exe scripts\backfill_blockchain_evidence.py
```

El proceso es idempotente: no duplica evidencias existentes y valida la cadena al finalizar.

## Error 429 en login

Esperar un minuto o usar credenciales correctas. Es una proteccion in-process de prototipo.
