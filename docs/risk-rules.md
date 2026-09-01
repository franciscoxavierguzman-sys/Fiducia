# Reglas de Riesgo

Version: `rules-v1`.

Todas las reglas viven en `backend/app/risk/rules.py`, son identificables, explicables y testeables.

| Regla | Severidad | Contribucion | Criterio |
| --- | --- | ---: | --- |
| R001 Monto inusual | HIGH | 18 | Monto >= 3 veces promedio historico |
| R002 Alta velocidad 24h | HIGH | 18 | 3 o mas remesas previas en 24 horas |
| R003 Alta velocidad 7d | MEDIUM | 12 | 5 o mas remesas previas en 7 dias |
| R004 Beneficiario nuevo | MEDIUM | 10 | Beneficiario nuevo o sin historial |
| R005 Corredor nuevo | MEDIUM | 10 | Primer uso del corredor por usuario |
| R006 Horario atipico | LOW | 6 | Operacion entre 00:00 y 05:59 |
| R007 Incremento abrupto | HIGH | 16 | Monto >= 2 veces maximo historico |
| R008 Diversidad reciente | MEDIUM | 10 | 3 o mas paises destino en 30 dias |
| R009 Fallas previas | MEDIUM | 10 | Ratio de fallas historicas >= 25% |
| R010 Combinacion conductual | HIGH | 16 | Beneficiario nuevo + actividad reciente + monto alto |

El score se suma y se acota a 100. No se usa pais o nacionalidad como senal directa de fraude.
