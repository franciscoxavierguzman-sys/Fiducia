# Assistant Architecture

FIDUCIA implementa un asistente read-only sobre servicios internos existentes.

```text
question -> auth -> intent router -> tool registry -> authorized retrieval -> minimal context -> provider -> response -> audit/persistence
```

El asistente no consulta HTTP contra la propia API. Reutiliza repositorios y servicios de remesas, BI, forecasting, riesgo y blockchain.

## Componentes

- `backend/app/assistant/router.py`: intent routing deterministico.
- `backend/app/assistant/tools.py`: registry de tools internas con roles permitidos.
- `backend/app/assistant/providers.py`: abstraccion `LLMProvider`, deterministic provider y external provider opcional.
- `backend/app/assistant/service.py`: orquestacion, ownership, persistencia, fallback, auditoria y provenance.
- `backend/app/assistant/prompt.py`: builder central de prompt y policy.

## Read-Only

No crea remesas, no completa pagos, no edita beneficiarios, no cambia evaluaciones, no recalcula riesgo, no modifica blockchain ni forecast.
