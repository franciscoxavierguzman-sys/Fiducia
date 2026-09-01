# Assistant Prompt Injection

El intent router detecta patrones basicos de:

- escalacion de rol;
- solicitud de system prompt;
- instrucciones para ignorar reglas;
- solicitud de todos los clientes.

Cuando se detectan, el intent se enruta a `OUT_OF_SCOPE`, no se ejecutan tools sensibles y se responde de forma segura.

La proteccion principal no depende del proveedor: la autorizacion ocurre antes de retrieval.
