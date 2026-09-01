# Blockchain Verification

## Chain Validation

`validate_chain()` verifica:

1. Genesis valido.
2. Indices consecutivos.
3. `previous_hash` correcto.
4. `block_hash` recalculado coincide.
5. PoW satisface dificultad.
6. `evidence_hash` tiene formato SHA-256.
7. `schema_version` soportado.
8. Timestamps parseables.

## Evidence Verification

`verify_evidence()` reconstruye el snapshot off-chain, lo canonicaliza, recalcula SHA-256 y compara contra el bloque.

Para evidencia de riesgo, la identidad idempotente se basa en `risk_assessment_id`, de modo que varias evaluaciones de una misma remesa puedan generar evidencias distintas. La verificacion de historial por remesa conserva `entity_reference = remittance_id` para consultar los bloques relacionados.

Estados:

- `VERIFIED`
- `MISMATCH`
- `NOT_FOUND`
- `UNSUPPORTED_SCHEMA`
