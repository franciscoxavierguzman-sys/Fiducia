# Matriz de autorizacion

| Feature | CLIENT | SUPPORT | RISK_ANALYST | ADMIN |
|---|---:|---:|---:|---:|
| Registro/login | Si | Si | Si | Si |
| Perfil propio | Si | Si | Si | Si |
| Administrar usuarios | No | Si | No | Si |
| Reiniciar contrasenas | No | Si | No | Si |
| Bloquear/desbloquear usuarios | No | Si | No | Si |
| Beneficiarios propios | Si | No | Si | Si |
| Metodos de pago propios | Si | No | Si | Si |
| Cotizar remesa | Si | No | Si | Si |
| Crear remesa propia | Si | No | Si | Si |
| Ver remesas propias | Si | No | Si | Si |
| Recibir remesa propia | Si | No | Si | Si |
| Tracking propio | Si | No | Si | Si |
| Risk dashboard | No | No | Si | Si |
| Ver evaluaciones de riesgo | No | No | Si | Si |
| Revisar evaluacion | No | No | Si | Si |
| ML model info/metrics | No | No | Si | Si |
| Forecast | No | No | Si | Si |
| BI dashboards | No | No | Si | Si |
| BI exports | No | No | Si | Si |
| Blockchain evidencia propia | Si | No | Si | Si |
| Blockchain explorer | No | No | Si | Si |
| Blockchain validate chain | No | No | No | Si |
| Assistant ayuda propia | Si | No | Si | Si |
| Assistant BI/risk/forecast | No | No | Si | Si |
| System info/metrics | No | No | No | Si |
| Audit directo | No | No endpoint publico | No | No endpoint publico |

Principio: un `CLIENT` nunca debe obtener recursos de otro usuario por conocer IDs. Los perfiles internos acceden a vistas agregadas o de revision cuando el modulo lo requiere.
`SUPPORT` se limita a actividades de mesa de ayuda: gestion de usuarios, recuperacion de acceso y desbloqueo. No debe ver remesas, pagos, dashboard, analitica, riesgo ni blockchain.
