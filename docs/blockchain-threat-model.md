# Blockchain Threat Model

## Amenazas Reducidas

- Modificacion posterior detectable de evidencia.
- Inconsistencia entre eventos relevantes de remesa.
- Alteracion accidental del historial encadenado.
- Perdida de trazabilidad verificable.

## Amenazas No Resueltas

- Fraude financiero por si solo.
- Robo de credenciales.
- Identidad falsa.
- Malware o compromiso del servidor.
- Errores en el dato original.
- Coordinacion distribuida entre multiples servidores.
- Prevencion absoluta de forks bajo multiples writers fuera del proceso local.
- KYC/AML real.
- Sanciones.
- Dinero ilicito.

## Principio Central

Blockchain protege integridad de evidencia; no garantiza que el dato original sea verdadero.

En otras palabras: garbage in, garbage forever. Si el evento original se registra con datos incorrectos, el hash solo demuestra que esos datos no cambiaron posteriormente.

La implementacion actual serializa escrituras con un lock local de proceso. Esto reduce carreras en la demo local, pero una version productiva requeriria controles transaccionales o un provider blockchain con garantias externas.
