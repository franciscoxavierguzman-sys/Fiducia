# FIDUCIA Fase 9 - Asistente Inteligente

## Problema

FIDUCIA ya posee remesas, riesgo, forecasting, BI y trazabilidad blockchain. El usuario necesita una capa conversacional que permita consultar esas capacidades con lenguaje natural sin crear una fuente paralela de verdad.

## Objetivos

- Implementar un asistente read-only.
- Respetar roles y ownership antes de recuperar datos.
- Reutilizar servicios internos existentes.
- Funcionar offline con un proveedor deterministico.
- Preparar una abstraccion opcional para proveedor externo.
- Registrar provenance, sources, tools y auditoria.
- Evitar acciones financieras o decisiones automaticas de riesgo.

## Alcance

Incluye soporte general, consultas de remesas propias, BI, forecasting, explicacion de riesgo y verificacion blockchain. No incluye pagos por chat, creacion de remesas, edicion de datos, RAG complejo, vector DB, internet, voice, WhatsApp, email ni entrenamiento de modelos.

## Casos De Uso

- CLIENT consulta ultima remesa, estado, comision y ayuda de uso.
- RISK_ANALYST consulta cola de riesgo y explicaciones de assessments.
- ADMIN consulta KPIs, forecast y estado blockchain.

## Arquitectura

```text
User question
  -> auth user/role
  -> intent router
  -> tool registry
  -> authorization before retrieval
  -> internal service/query
  -> minimal structured context
  -> prompt builder
  -> provider deterministic/external
  -> response validation
  -> conversation persistence
  -> audit
```

## Roles

- CLIENT: soporte y datos propios.
- RISK_ANALYST: soporte, riesgo, BI permitida y blockchain de auditoria.
- ADMIN: soporte, BI, forecasting, riesgo y blockchain.

## Intents

`GENERAL_HELP`, `MY_REMITTANCES`, `REMITTANCE_STATUS`, `REMITTANCE_FEES`, `BI_OVERVIEW`, `BI_CORRIDORS`, `BI_CUSTOMERS`, `FORECAST_SUMMARY`, `RISK_QUEUE`, `RISK_EXPLANATION`, `BLOCKCHAIN_TRACE`, `BLOCKCHAIN_VERIFY`, `OUT_OF_SCOPE`.

## Tools Internos

`get_my_remittances`, `get_remittance_status`, `get_remittance_fee`, `get_bi_overview`, `get_top_corridors`, `get_forecast_summary`, `get_risk_queue`, `get_risk_assessment`, `get_blockchain_trace`, `verify_blockchain_evidence`, `get_support_article`.

## LLM Abstraction

`LLMProvider` define `generate`, `generate_structured` y `health_check`. `DeterministicAssistantProvider` es el proveedor por defecto para pruebas y demo offline. `ExternalLLMProvider` es opcional y depende de variables de entorno, sin API keys en codigo.

## Grounding

Las respuestas deben incluir `tools_used`, `sources`, `source_types`, `intent` y metadata de proveedor. El proveedor recibe solo contexto minimo autorizado.

## Seguridad

La autorizacion ocurre antes de recuperar datos. CLIENT nunca consulta datos de otros usuarios. Intentos de escalacion de rol, prompt injection o solicitud de system prompt se enrutan a respuestas seguras sin retrieval sensible.

## Privacidad

Se persisten mensajes de usuario y respuesta, intent, tools, sources y metadata. No se almacena razonamiento interno, system prompt, JWT, password, datos completos de tarjeta, CVV ni credenciales de funding.

## Conversation Storage

`assistant_conversations` pertenece a un usuario. `assistant_messages` guarda mensajes user/assistant, intent, provider, tools y sources. Un usuario solo puede leer sus conversaciones.

## Auditoria

Eventos: `ASSISTANT_CONVERSATION_CREATED`, `ASSISTANT_MESSAGE_RECEIVED`, `ASSISTANT_TOOL_USED`, `ASSISTANT_RESPONSE_GENERATED`, `ASSISTANT_PROVIDER_FAILED`, `ASSISTANT_ACCESS_DENIED`.

## Frontend

Vista `Asistente` disponible para CLIENT, RISK_ANALYST y ADMIN. Incluye historial, sugerencias por rol, input, loading, errores, fuentes discretas y nueva conversacion.

## Testing

Tests unitarios y de API para autorizacion, ownership, prompt injection, system prompt, hallucination, fidelidad numerica, riesgo, forecast, blockchain, fallback, minimizacion y conversaciones.

## Evaluacion

Dataset controlado en `reports/assistant/evaluation_cases.json`. Metricas: intent accuracy, tool selection accuracy, authorization success, grounded answer, numeric fidelity, hallucination, unsafe actions.

## Limitaciones

El proveedor deterministico no es IA generativa real. El proveedor externo es opcional y no se prueba sin configuracion. No hay rate limiting distribuido ni eliminacion de conversaciones en esta fase.

## Criterios De Aceptacion

Fase 9 se acepta si el asistente funciona offline, respeta permisos, reutiliza servicios internos, persiste conversaciones, registra auditoria, incluye frontend, pasa evaluacion controlada, suite backend y build frontend.
