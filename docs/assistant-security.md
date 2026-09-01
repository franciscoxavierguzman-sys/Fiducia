# Assistant Security

## Authorization Before Retrieval

El asistente deriva rol desde `current_user`. El cliente no puede declarar `role=ADMIN` ni seleccionar permisos por payload.

Para CLIENT, las remesas se consultan mediante filtros por `current_user.id`. Si el usuario conoce un `remittance_number` ajeno, el backend verifica ownership antes de devolver contexto.

## Forbidden Actions

El asistente no ejecuta pagos, no crea remesas, no aprueba ni rechaza riesgo, no modifica scores, no cambia blockchain y no edita datos maestros.

## Audit

Eventos principales:

- `ASSISTANT_CONVERSATION_CREATED`
- `ASSISTANT_MESSAGE_RECEIVED`
- `ASSISTANT_TOOL_USED`
- `ASSISTANT_RESPONSE_GENERATED`
- `ASSISTANT_PROVIDER_FAILED`
- `ASSISTANT_ACCESS_DENIED`

No se registran secretos ni tokens.
