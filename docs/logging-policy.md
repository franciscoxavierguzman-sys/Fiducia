# Politica de logging

Los logs de FIDUCIA son tecnicos y proporcionales al prototipo. Deben facilitar diagnostico sin exponer datos sensibles.

## Permitido

- `request_id`
- metodo HTTP
- ruta
- codigo de respuesta
- duracion
- evento tecnico
- `user_id` cuando sea necesario y no sustituya auditoria
- entidad y referencia no sensible

## No permitido

- contrasenas
- JWT o Bearer tokens
- CVV
- numero completo de cuenta o tarjeta
- documento completo
- llaves de proveedor externo
- prompts internos del asistente
- stack traces en respuestas al usuario

## Auditoria

La auditoria registra eventos de negocio relevantes: login, remesa, riesgo, blockchain, asistente y revisiones. No se audita cada `GET` de lectura rutinaria.

## Correlacion

Cada request recibe `X-Request-ID`. Si el cliente envia uno, se preserva. Si no, se genera un UUID.
