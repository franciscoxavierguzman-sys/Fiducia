# Assistant Privacy

## Conversaciones

`assistant_conversations` pertenece a un `user_id`. `assistant_messages` almacena mensajes visibles, intent, provider, tools, sources, eventos de seguridad y metadata.

No se almacena chain-of-thought ni prompts internos. No se almacenan contrasenas, JWT, CVV, numeros completos de tarjetas, credenciales de funding ni system prompts.

## Acceso

Un usuario solo puede leer sus propias conversaciones. ADMIN no recibe acceso automatico al contenido privado completo de otros usuarios.

## Retencion

La retencion es simple para el prototipo: las conversaciones quedan activas en base operacional. Eliminacion o politicas legales formales quedan fuera de Fase 9.
