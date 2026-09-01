# Blockchain Future Integration

La interfaz `BlockchainProvider` permitiria reemplazar `LocalBlockchainProvider` por un provider EVM, Besu o LACChain.

## Evolucion Conceptual

- Adapter RPC.
- Smart contract opcional para registrar `evidence_hash`.
- Transaction hash on-chain como prueba externa.
- Confirmaciones de red.
- Manejo de gas.
- Politicas de privacidad.
- Reintentos ante fallos de red.

No se implementa conexion real en Fase 8.
