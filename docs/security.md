# Seguridad y privacidad

La Fase 1 implementa controles proporcionales a un prototipo academico:

- contrasenas hasheadas con bcrypt;
- autenticacion con JWT;
- roles base: `sender`, `risk_analyst`, `admin`;
- endpoints protegidos mediante bearer token;
- validacion de entrada con Pydantic;
- configuracion sensible mediante variables de entorno.

## Limitaciones

FIDUCIA no implementa aun rate limiting, rotacion de secretos, auditoria completa ni politicas avanzadas de sesion. Estos controles quedan para fases posteriores de hardening.

## Privacidad

La aplicacion debe usar datos ficticios o sinteticos. No deben registrarse documentos reales, cuentas reales, tarjetas reales ni informacion financiera sensible real.
