# Matriz de autorizacion

| Feature | CLIENT | RISK_ANALYST | ADMIN |
|---|---:|---:|---:|
| Registro/login | Si | Si | Si |
| Perfil propio | Si | Si | Si |
| Beneficiarios propios | Si | Si | Si |
| Metodos de pago propios | Si | Si | Si |
| Cotizar remesa | Si | Si | Si |
| Crear remesa propia | Si | Si | Si |
| Ver remesas propias | Si | Si | Si |
| Recibir remesa propia | Si | Si | Si |
| Tracking propio | Si | Si | Si |
| Risk dashboard | No | Si | Si |
| Ver evaluaciones de riesgo | No | Si | Si |
| Revisar evaluacion | No | Si | Si |
| ML model info/metrics | No | Si | Si |
| Forecast | No | Si | Si |
| BI dashboards | No | Si | Si |
| BI exports | No | Si | Si |
| Blockchain evidencia propia | Si | Si | Si |
| Blockchain explorer | No | Si | Si |
| Blockchain validate chain | No | No | Si |
| Assistant ayuda propia | Si | Si | Si |
| Assistant BI/risk/forecast | No | Si | Si |
| System info/metrics | No | No | Si |
| Audit directo | No | No | No endpoint publico |

Principio: un `CLIENT` nunca debe obtener recursos de otro usuario por conocer IDs. Los perfiles internos acceden a vistas agregadas o de revision cuando el modulo lo requiere.
