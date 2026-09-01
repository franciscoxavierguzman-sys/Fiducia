# Blockchain Architecture

FIDUCIA implementa una blockchain local demostrativa mediante adapter.

```
Domain Event
  -> Evidence Builder
  -> canonicalize()
  -> sha256_hex()
  -> BlockchainProvider.record_evidence()
  -> LocalBlockchainProvider
  -> blockchain_blocks
```

## Provider

`BlockchainProvider` define:

- `record_evidence`
- `verify_evidence`
- `get_block`
- `get_chain`
- `validate_chain`
- `get_entity_history`

`LocalBlockchainProvider` es la implementacion inicial sobre SQLite.

La escritura de bloques usa un lock local de proceso para serializar la lectura del ultimo bloque, el calculo de `previous_hash`, el minado y la insercion. Esta medida evita carreras dentro de una instancia local, pero no es un mecanismo distribuido.

## Separacion De Responsabilidades

Remesas y Risk Engine producen eventos. Blockchain registra evidencia. Blockchain no calcula riesgo, no aprueba, no rechaza y no mueve dinero.

Si la capa blockchain falla al registrar evidencia, el servicio captura el error, lo registra en auditoria y no destruye la remesa ni la evaluacion de riesgo principal.
