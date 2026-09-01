# Flujo de Revision de Riesgo

Roles permitidos:

- `ADMIN`
- `RISK_ANALYST`

`CLIENT` recibe 403 en endpoints internos de riesgo.

## Flujo

1. Cliente crea una remesa.
2. El backend crea un `risk_assessment`.
3. La remesa mantiene su estado operacional normal.
4. Analista abre "Revision de riesgo".
5. Analista revisa reglas, ML, anomalia, score final y explicaciones.
6. Analista registra decision:
   - APPROVE
   - ESCALATE
   - REJECT
7. `ESCALATE` y `REJECT` requieren justificacion.
8. Se registra auditoria.

Estas decisiones son internas del prototipo y no representan decisiones regulatorias reales.

`HIGH` significa senales de riesgo elevadas que requieren revision humana. No significa fraude confirmado y no bloquea automaticamente la remesa.
