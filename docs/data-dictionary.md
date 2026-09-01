# Diccionario de datos - FIDUCIA Fase 3

Dataset principal: `data/processed/remittances_analytics.csv`.

## Variables

| Variable | Tipo | Descripcion | Fuente | Transformacion | Unidad/rango | Uso futuro |
| --- | --- | --- | --- | --- | --- | --- |
| user_id | string | ID sintetico anonimizado del usuario remitente | Generador sintetico | Secuencia `USR-000000` | No PII | Agrupacion de comportamiento |
| country | string | Pais del usuario | Generador sintetico | Catalogo controlado | Pais activo | Segmentacion |
| account_age_days | integer | Antiguedad de cuenta al momento de la remesa | Generador sintetico | `created_at - registration_date` | Dias >= 0 | Riesgo/comportamiento |
| transaction_count | integer | Remesas historicas previas del usuario | Feature engineering | Conteo acumulado | >= 0 | Velocidad y madurez |
| historical_amount | decimal | Monto historico acumulado previo | Feature engineering | Suma previa | Moneda origen historica mixta | Perfil transaccional |
| registration_date | date | Fecha sintetica de registro | Generador sintetico | ISO date | Fecha | Antiguedad |
| remittance_id | string | ID sintetico unico de remesa | Generador sintetico | Secuencia seed + contador | Unico | Llave analitica |
| remittance_number | string | Numero visible sintetico | Generador sintetico | Formato `FID-YYYY-000000` | Unico | Trazabilidad |
| origin_country | string | Pais origen | Generador sintetico | Catalogo controlado | Pais activo | Corredores |
| destination_country | string | Pais destino | Generador sintetico | Distinto de origen | Pais activo | Corredores |
| source_currency | string | Moneda origen | Catalogo pais | Mapeo por pais | ISO 4217 | Calculos |
| destination_currency | string | Moneda destino | Catalogo pais | Mapeo por pais | ISO 4217 | Calculos |
| source_amount | decimal | Monto enviado | Generador sintetico | Distribucion lognormal | 10.00 a 5000.00 | Ticket y riesgo |
| commission_rate | decimal | Tasa de comision | Generador sintetico | 1.8 % a 3.6 % | 0.018000 a 0.036000 | Ingresos |
| commission_amount | decimal | Comision cobrada | Calculo | `source_amount * commission_rate` | Moneda origen | Ingresos |
| total_debit_amount | decimal | Total debitado | Calculo | `source_amount + commission_amount` | Moneda origen | Validacion financiera |
| exchange_rate | decimal | Tipo de cambio aplicado | Calculo sintetico | Relacion por moneda contra USD | > 0 | FX |
| destination_amount | decimal | Monto estimado recibido | Calculo | `source_amount * exchange_rate` | Moneda destino | Pago |
| delivery_method | string | Metodo de entrega | Generador sintetico | Catalogo | BANK_DEPOSIT, TRANSFER, WALLET, CASH_PICKUP | Preferencias |
| funding_method | string | Metodo de fondeo | Generador sintetico | Catalogo | BANK_TRANSFER, DEBIT_CARD, DIGITAL_WALLET | Preferencias |
| status | string | Estado de remesa | Generador sintetico | Distribucion ponderada | AVAILABLE, COMPLETED, PROCESSING, REVIEW_REQUIRED, REJECTED | Funnel operativo |
| created_at | datetime | Fecha de creacion | Generador sintetico | ISO datetime | Fecha/hora | Series temporales |
| completed_at | datetime nullable | Fecha de cierre | Generador sintetico | Solo para COMPLETED | Fecha/hora | Tiempos de ciclo |
| beneficiary_id | string | ID sintetico de beneficiario | Generador sintetico | Secuencia `BEN-000000` | No PII | Relaciones |
| relationship | string | Relacion con beneficiario | Generador sintetico | Catalogo | Texto | Segmentacion |
| linked_user | integer | Indicador de beneficiario vinculado a usuario | Generador sintetico | 0/1 | Binario | Pago/recepcion |
| transactions_last_24h | integer | Transacciones previas en 24h | Feature engineering | Ventana movil | >= 0 | Velocidad |
| transactions_last_7d | integer | Transacciones previas en 7 dias | Feature engineering | Ventana movil | >= 0 | Velocidad |
| transactions_last_30d | integer | Transacciones previas en 30 dias | Feature engineering | Ventana movil | >= 0 | Frecuencia |
| avg_transaction_amount | decimal | Promedio historico previo | Feature engineering | Media acumulada | >= 0 | Cambio de monto |
| max_transaction_amount | decimal | Maximo historico previo | Feature engineering | Max acumulado | >= 0 | Cambio de monto |
| new_beneficiary | integer | Beneficiario reciente | Feature engineering | Antiguedad <= 7 dias | 0/1 | Riesgo futuro |
| beneficiary_age_days | integer | Antiguedad del beneficiario | Feature engineering | `created_at - beneficiary.created_at` | Dias >= 0 | Riesgo futuro |
| countries_used_last_30d | integer | Paises destino usados en 30 dias | Feature engineering | Conteo distinto | >= 0 | Diversidad |
| failed_transactions | integer | Operaciones previas no exitosas | Feature engineering | Conteo acumulado | >= 0 | Riesgo futuro |
| transaction_hour | integer | Hora de operacion | Feature engineering | `created_at.hour` | 0 a 23 | Horarios atipicos |
| weekend_transaction | integer | Indicador fin de semana | Feature engineering | Sabado/domingo | 0/1 | Patrones |
| amount_vs_user_average | decimal | Relacion monto actual vs promedio | Feature engineering | `source_amount / historical_avg_amount` | >= 0 | Anomalias |
| transaction_velocity_24h | integer | Alias analitico de velocidad 24h | Feature engineering | Ventana movil | >= 0 | ML futuro |
| transaction_velocity_7d | integer | Alias analitico de velocidad 7d | Feature engineering | Ventana movil | >= 0 | ML futuro |
| new_beneficiary_flag | integer | Alias binario de beneficiario nuevo | Feature engineering | 0/1 | Binario | ML futuro |
| unusual_hour_flag | integer | Horario atipico | Feature engineering | Hora 0 a 5 | 0/1 | ML futuro |
| weekend_flag | integer | Alias fin de semana | Feature engineering | 0/1 | Binario | ML futuro |
| new_corridor_flag | integer | Primer uso de corredor por usuario | Feature engineering | 0/1 | Binario | ML futuro |
| country_diversity_30d | integer | Diversidad de destino reciente | Feature engineering | Conteo distinto | >= 0 | ML futuro |
| failed_transaction_ratio | decimal | Proporcion de fallas previas | Feature engineering | Fallas / transacciones previas | 0 a 1 aprox. | ML futuro |
| historical_avg_amount | decimal | Promedio historico base | Feature engineering | Media acumulada | >= 0 | ML futuro |
| historical_max_amount | decimal | Maximo historico base | Feature engineering | Max acumulado | >= 0 | ML futuro |
| rule_score | decimal | Puntaje experimental sintetico | Generador sintetico | Combinacion de senales | 0 a 99 | Investigacion futura |
| ml_probability | decimal | Probabilidad placeholder experimental | Generador sintetico | Derivada de rule_score | 0 a 1 | Fase 4 |
| anomaly_score | decimal | Puntaje de anomalia placeholder | Generador sintetico | Ruido + senales | 0 a 1 | Fase 4 |
| final_risk_score | decimal | Puntaje final experimental | Generador sintetico | Mezcla sintetica | 0 a 99 | Fase 4 |
| fraud_label | integer | Etiqueta sintetica de potencial fraude | Generador sintetico | Distribucion configurable | 0/1 | Entrenamiento futuro |
| amount_bucket | string | Rango de monto | Pipeline | Bucketing | 0-99, 100-499, 500-999, 1000-2499, 2500+ | Analitica |
| risk_band_experimental | string | Banda experimental de riesgo | Pipeline | final_risk_score | BAJO, MEDIO, ALTO | Exploracion |
| is_cross_border | integer | Indicador de corredor internacional | Pipeline | Origen distinto de destino | 1 en dataset actual | Validacion |

## Privacidad

El dataset no contiene contrasenas, JWT, CVV, numeros completos de tarjeta, numeros completos de cuenta bancaria, PIN, credenciales ni secretos.

## Variables Fase 5

| Variable | Tipo | Descripcion |
| --- | --- | --- |
| risk_assessment.rule_score | decimal nullable | Score de reglas 0-100 |
| risk_assessment.ml_probability | decimal nullable | Probabilidad ML original 0-1 |
| risk_assessment.anomaly_score | decimal nullable | Score de anomalia 0-100 |
| risk_assessment.final_risk_score | decimal nullable | Score agregado 0-100 |
| risk_assessment.risk_band | string | LOW, MEDIUM, HIGH o UNKNOWN |
| risk_assessment.recommended_action | string | CONTINUE, REVIEW, MANUAL_REVIEW |
| risk_assessment.signal_status_json | JSON | Disponibilidad de cada senal |
| risk_assessment.triggered_rules_json | JSON | Reglas activadas y razones |
| risk_assessment.review_decision | string nullable | APPROVE, ESCALATE o REJECT |

## Variables Fase 6

| Variable | Tipo | Descripcion |
| --- | --- | --- |
| period | date | Inicio de semana del periodo agregado |
| transaction_count | integer | Remesas por semana |
| transaction_amount_usd | decimal | Monto semanal agregado en USD equivalente |
| forecast.predicted | decimal | Valor estimado futuro |
| forecast.lower_80 | decimal nullable | Limite inferior experimental 80% |
| forecast.upper_80 | decimal nullable | Limite superior experimental 80% |
| forecast.lower_95 | decimal nullable | Limite inferior experimental 95% |
| forecast.upper_95 | decimal nullable | Limite superior experimental 95% |

## Uso en Fase 4

Las features incluidas y excluidas para ML se documentan en `docs/phase4-ml-plan.md`. En particular, `rule_score`, `ml_probability`, `anomaly_score`, `final_risk_score`, `risk_band_experimental`, `status` y `completed_at` no se usan como features de entrenamiento para evitar leakage.

## Variables Fase 7

| Variable | Tipo | Descripcion |
| --- | --- | --- |
| total_remittances | integer | Conteo de remesas filtradas |
| total_amount_usd_equivalent | decimal | Monto origen convertido a USD equivalente |
| average_ticket_usd_equivalent | decimal nullable | Monto USD equivalente promedio por remesa |
| total_commission_revenue_usd_equivalent | decimal | Comisiones historicas convertidas a USD equivalente |
| average_commission_usd_equivalent | decimal nullable | Comision promedio por remesa |
| active_clients | integer | Remitentes con actividad en el periodo |
| active_corridors | integer | Pares origen-destino con actividad |
| completion_rate | decimal nullable | Remesas completadas / remesas elegibles |
| repeat_sender_rate | decimal nullable | Clientes activos con mas de una remesa / clientes activos |
| risk_distribution | array | Distribucion agregada LOW, MEDIUM, HIGH desde risk_assessments |
| forecast_outlook | object | Resumen de remittance-forecast-v1 para BI |

## Variables Fase 8

| Variable | Tipo | Descripcion |
| --- | --- | --- |
| blockchain.block_index | integer | Posicion secuencial del bloque dentro de la cadena local |
| blockchain.event_type | string | Evento operativo registrado |
| blockchain.entity_type | string | Tipo de entidad evidenciada: remittance, risk_assessment o system |
| blockchain.entity_reference | string | Referencia interna no sensible de la entidad |
| blockchain.evidence_hash | string | SHA-256 del payload canonico de evidencia |
| blockchain.previous_hash | string | Hash del bloque anterior |
| blockchain.block_hash | string | SHA-256 del encabezado canonico del bloque |
| blockchain.nonce | integer | Nonce usado para cumplir la dificultad configurada |
| blockchain.difficulty | integer | Cantidad de ceros iniciales requeridos en la prueba de trabajo local |
| blockchain.schema_version | string | Version del esquema de evidencia |
| blockchain.idempotency_key | string | Clave deterministica para evitar duplicar el mismo evento |
| blockchain.record_status | string | Estado de registro del bloque |
| blockchain.mining_time_ms | integer | Tiempo local aproximado de minado |

La evidencia blockchain excluye PII y datos sensibles. Para remesas se registran identificadores internos, paises, monedas, montos, estado y fecha canonica. Para riesgo se registran versiones, scores agregados, banda de riesgo y accion recomendada, manteniendo `ml_probability` separada de la clasificacion.

La idempotencia de riesgo usa `risk_assessment_id` como identidad estable para permitir multiples evaluaciones validas de una misma remesa sin duplicar la misma evaluacion.

## Variables Fase 9

| Variable | Tipo | Descripcion |
| --- | --- | --- |
| assistant.intent | string | Intent detectado por router deterministico |
| assistant.provider | string | Proveedor utilizado: deterministic o external con fallback |
| assistant.tools_used_json | JSON | Tools internas ejecutadas |
| assistant.sources_json | JSON | Fuentes autorizadas usadas para grounding |
| assistant.safety_events_json | JSON | Eventos como prompt injection o escalacion de rol |
| assistant.metadata_json | JSON | Metadata de respuesta sin secretos |
| assistant.conversation.user_id | integer | Propietario de la conversacion |

El contexto enviado al provider se minimiza por intent y rol. No incluye password, JWT, datos completos de tarjeta, CVV, documentos ni detalles bancarios innecesarios.
