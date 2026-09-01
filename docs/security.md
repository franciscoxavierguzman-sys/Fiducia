# Seguridad y privacidad

FIDUCIA implementa controles proporcionales a un prototipo local integrado:

- contrasenas hasheadas con bcrypt;
- autenticacion con JWT;
- roles base: `CLIENT`, `RISK_ANALYST`, `ADMIN`;
- endpoints protegidos mediante bearer token;
- validacion de entrada con Pydantic;
- configuracion sensible mediante variables de entorno.
- request ID por request;
- headers HTTP basicos;
- rate limiting in-process para login y asistente;
- auditoria de eventos relevantes.

## Limitaciones

FIDUCIA no implementa rotacion automatica de secretos, gestor productivo de secretos, rate limiting distribuido, politicas avanzadas de sesion ni monitoreo externo. Estos controles quedan documentados como mejoras futuras.

## Privacidad

La aplicacion debe usar datos ficticios o sinteticos. No deben registrarse documentos reales, cuentas reales, tarjetas reales ni informacion financiera sensible real.
