# FIDUCIA Fase 8 - Blockchain, Trazabilidad E Integridad Verificable

## Problema

FIDUCIA necesita demostrar que ciertos eventos relevantes de una remesa no fueron alterados despues de ocurrir. La base de datos operacional conserva el dato de negocio, mientras que blockchain actua como capa de evidencia verificable.

## Objetivo

Implementar una blockchain local demostrativa para hashing, encadenamiento, prueba de trabajo simple, trazabilidad, verificacion e inmutabilidad detectable.

## Arquitectura

```
Remittance / Risk Assessment
  -> Domain Event
  -> Evidence Builder
  -> Canonical JSON
  -> SHA-256 evidence_hash
  -> LocalBlockchainProvider
  -> blockchain_blocks
  -> Verification
```

## Eventos

- `REMITTANCE_CREATED`
- `RISK_ASSESSMENT_RECORDED`
- `REMITTANCE_AVAILABLE`
- `REMITTANCE_COMPLETED`

`REMITTANCE_CONFIRMED` fue removido del catalogo activo porque el lifecycle actual no tiene un punto de dominio separado e inequivoco para confirmacion sin introducir un nuevo estado transaccional.

## Canonicalization

La evidencia se serializa como JSON canonico con claves ordenadas, UTF-8, separadores compactos y normalizacion de `Decimal` y fechas. Se excluyen campos no deterministas y PII.

## Hashing

Se usa `hashlib.sha256`. El hash de evidencia es el SHA-256 del JSON canonico.

## Estructura De Bloque

Campos principales:

- `block_index`
- `timestamp`
- `event_type`
- `entity_type`
- `entity_reference`
- `evidence_hash`
- `previous_hash`
- `nonce`
- `difficulty`
- `block_hash`
- `schema_version`
- `idempotency_key`
- `record_status`
- `mining_time_ms`

## Almacenamiento

Persistencia SQLAlchemy en `blockchain_blocks`. No se crea un data warehouse ni se guarda el payload completo en cadena.

## Privacidad

No se almacena nombre, apellido, email, telefono, documento, cuenta, tarjeta, banco, contrasena, token ni JWT.

## Verificacion

`validate_chain()` recalcula hashes, revisa indices, previous_hash, PoW, schemas y hashes de evidencia. `verify_evidence()` reconstruye snapshot off-chain y compara con `evidence_hash`.

## Threat Model

Reduce manipulacion posterior detectable de evidencias, inconsistencia historica y alteracion accidental. No prueba que el dato original sea verdadero.

## API

- `GET /api/v1/blockchain/info`
- `GET /api/v1/blockchain/blocks`
- `GET /api/v1/blockchain/blocks/{block_index}`
- `GET /api/v1/blockchain/transactions/{remittance_id}/history`
- `GET /api/v1/blockchain/verify/{remittance_id}`
- `GET /api/v1/blockchain/validate`

## Frontend

Seccion administrativa `Trazabilidad blockchain`, con dashboard, explorer, detalle de bloque, trazabilidad de remesa y vista educativa de verificacion.

## Pruebas

Tests unitarios para canonicalization, SHA-256, genesis, PoW, encadenamiento, tampering, verification, idempotencia, permisos y privacidad.

## Limitaciones

Blockchain local no es descentralizada ni equivalente a Bitcoin/Ethereum. SQLite puede ser alterado externamente. La capa detecta cambios de evidencia, pero no garantiza veracidad de datos originales.

`LocalBlockchainProvider` usa un lock local para serializar escrituras dentro de una instancia/proceso. No garantiza coordinacion distribuida entre multiples servidores.

Si falla el registro blockchain, se registra auditoria `BLOCKCHAIN_EVIDENCE_FAILED` y el flujo principal continua. No existe retry persistente automatico en esta fase.

## Criterios De Aceptacion

Blockchain local append-only, eventos reducidos, sin PII, con tests, API protegida, explorer funcional, sin modificar modelos de riesgo, forecasting o BI.
