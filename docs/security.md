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
- CORS local con lista explicita de origins autorizados.

## Limitaciones

FIDUCIA no implementa rotacion automatica de secretos, gestor productivo de secretos, rate limiting distribuido, politicas avanzadas de sesion, monitoreo externo ni politica CORS productiva definitiva. Estos controles quedan documentados como mejoras futuras.

## CORS local

Para desarrollo se autorizan `http://localhost:5173` y `http://127.0.0.1:5173`. No se configura `allow_origins=["*"]` con credenciales.

## Privacidad

La aplicacion debe usar datos ficticios o sinteticos. No deben registrarse documentos reales, cuentas reales, tarjetas reales ni informacion financiera sensible real.
