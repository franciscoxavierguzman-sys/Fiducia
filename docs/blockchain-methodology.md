# Blockchain Methodology

## Canonicalization

El payload se normaliza con:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

Antes de serializar se normalizan `Decimal`, fechas, listas y diccionarios.

## SHA-256

`evidence_hash = SHA256(canonical_evidence_utf8)`

`block_hash = SHA256(canonical_block_header_utf8)`

## Proof Of Work

La dificultad por defecto es `2`. El `nonce` aumenta hasta que `block_hash` inicia con `difficulty` ceros. Es demostrativo y local, no seguridad equivalente a redes publicas.

## Idempotencia

Eventos de remesa:

```text
idempotency_key = entity_type:entity_reference:event_type:schema_version
```

Ejemplo:

```text
remittance:42:REMITTANCE_CREATED:remittance-evidence-v1
```

Eventos de riesgo:

```text
idempotency_key = risk_assessment:risk_assessment_id:event_type:schema_version
```

Ejemplo:

```text
risk_assessment:15:RISK_ASSESSMENT_RECORDED:risk-evidence-v1
```

Esto permite que una misma remesa tenga multiples evaluaciones de riesgo legitimas. El mismo `risk_assessment_id` registrado dos veces devuelve el bloque existente.

## Concurrencia Local

`LocalBlockchainProvider` serializa en memoria el bloque critico `get last block + mine + insert` mediante un lock local de proceso. Esta proteccion aplica dentro de una instancia de la aplicacion.

SQLite sigue siendo una eleccion apropiada para el prototipo local, pero no se afirma prevencion distribuida de forks entre multiples procesos o servidores. Una version productiva deberia usar transacciones/locking mas fuertes o un provider blockchain externo.

## Failure Behavior

Blockchain es una capa secundaria de evidencia. Si falla `record_evidence()`, la operacion principal registra un evento de auditoria `BLOCKCHAIN_EVIDENCE_FAILED` y conserva el flujo transaccional. No existe persistencia de retry automatico en esta fase; queda como deuda tecnica.
