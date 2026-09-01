# Assistant Provider

## Abstraccion

`LLMProvider` define:

- `generate()`
- `generate_structured()`
- `health_check()`

## Deterministic Provider

`DeterministicAssistantProvider` es el proveedor por defecto. Funciona offline, sin API key, sin internet y sin costo externo. No finge ser un LLM; genera respuestas utiles desde contexto estructurado.

## External Provider

`ExternalLLMProvider` es opcional mediante variables de entorno como `ASSISTANT_PROVIDER`, `ASSISTANT_MODEL` y `ASSISTANT_API_KEY`. No hay claves hardcodeadas.

Si falla, el servicio registra `ASSISTANT_PROVIDER_FAILED` y usa fallback deterministico.
