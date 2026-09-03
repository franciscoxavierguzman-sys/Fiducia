# API de FIDUCIA

La API usa el prefijo versionado `/api/v1`.

## Autenticacion

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/password/forgot
POST /api/v1/auth/password/change
GET  /api/v1/users/me
PATCH /api/v1/users/me
```

Los endpoints funcionales de Fase 2 requieren token Bearer.

El registro crea usuarios `CLIENT` y requiere confirmacion de contrasena, aceptacion de terminos, verificacion humana simulada, tipo de documento, numero de documento y fecha de nacimiento. Para `DPI`, el numero debe contener exactamente 13 digitos. Para `PASSPORT`, el numero acepta de 6 a 20 caracteres alfanumericos o guiones.

La recuperacion de contrasena genera una contrasena temporal para correos registrados, marca al usuario con cambio obligatorio y registra un correo simulado en `database/mail_outbox.jsonl`. En entorno local de demostracion la respuesta puede incluir la contrasena temporal para facilitar la prueba. Al iniciar sesion con esa contrasena, el frontend solicita definir una nueva antes de continuar.

## Catalogos

```text
GET /api/v1/catalogs/countries
GET /api/v1/catalogs/beneficiary-relationships
GET /api/v1/catalogs/departments
GET /api/v1/catalogs/departments/{id}/municipalities
```

## Beneficiarios

```text
GET   /api/v1/beneficiaries
POST  /api/v1/beneficiaries
GET   /api/v1/beneficiaries/{id}
PATCH /api/v1/beneficiaries/{id}
```

Decision: se implemento `PATCH` y no `PUT` para evitar endpoints redundantes en esta fase. La edicion de beneficiarios es parcial y la desactivacion logica puede enviarse como:

```json
{
  "is_active": false
}
```

Reglas:

- Solo se listan beneficiarios del usuario autenticado.
- No se permite consultar o modificar beneficiarios de otro usuario.
- `account_last_four` acepta solo cuatro digitos ficticios.
- Cada beneficiario incluye `country` y `currency`.
- El beneficiario debe corresponder al pais destino del corredor seleccionado.
- El campo opcional `email` permite vincular el beneficiario con una cuenta FIDUCIA existente.
- Si el correo corresponde a un usuario registrado, se resuelve `beneficiary_user_id`.

## Simulacion de remesas

```text
GET  /api/v1/remittances/corridors
POST /api/v1/remittances/simulate
```

Este endpoint no crea transacciones. Devuelve una cotizacion calculada por backend.

Cuando el destino es Guatemala y la moneda origen es `USD`, el backend intenta consultar el tipo de cambio vigente en `https://www.banguat.gob.gt/tipo_cambio`. Si la consulta no esta disponible, usa la tabla local `exchange_rates` como respaldo. La respuesta incluye `exchange_rate_source` para mostrar la fuente aplicada de forma discreta en la interfaz.

Para rutas `USD -> GTQ`, el monto de la remesa se mantiene expresado en `USD`, pero se permite seleccionar metodos de pago en `USD` o `GTQ`. Si el metodo de pago esta en `GTQ`, `total_debit_amount` se calcula convirtiendo el total en dolares, incluida la comision, con el tipo de cambio aplicado.

En el detalle de remesa, la interfaz normaliza monedas historicas incompletas para mostrar `Quetzales (GTQ)` cuando el destino es Guatemala. Tambien permite imprimir un comprobante con remitente, beneficiario, montos, tipo de cambio, metodo de pago, metodo de entrega y estado.

Campos principales:

```json
{
  "beneficiary_id": 1,
  "origin_country": "Estados Unidos",
  "destination_country": "Guatemala",
  "amount": "400.00",
  "currency": "USD",
  "payment_method": "BANK_TRANSFER",
  "delivery_method": "BANK_DEPOSIT"
}
```

## Transacciones

```text
GET  /api/v1/transactions
GET  /api/v1/transactions/sent
GET  /api/v1/transactions/received
POST /api/v1/transactions
GET  /api/v1/transactions/{id}
POST /api/v1/transactions/{id}/receive
```

`GET /api/v1/transactions` se mantiene como alias de remesas enviadas para compatibilidad.

Una nueva transaccion inicia en estado `AVAILABLE` durante esta fase para poder demostrar el ciclo:

```text
enviar -> disponible para recibir -> completar recepcion
```

`POST /api/v1/transactions/{id}/receive` solo permite la transicion `AVAILABLE -> COMPLETED` cuando el usuario autenticado coincide con `transaction.beneficiary_user_id`.

Si el beneficiario no tiene cuenta vinculada al momento del envio, la transaccion existe y queda en el historial del remitente. Cuando un usuario inicia sesion con el mismo correo registrado en el beneficiario, FIDUCIA vincula automaticamente esas remesas pendientes para que aparezcan en `Remesas recibidas` y puedan cobrarse.

## Metodos de pago

```text
GET   /api/v1/funding-sources
POST  /api/v1/funding-sources
PATCH /api/v1/funding-sources/{id}
POST  /api/v1/funding-sources/{id}/default
```

Solo se guardan datos de prueba y ultimos cuatro digitos. El metodo debe pertenecer al usuario, estar activo y coincidir con la moneda origen de la remesa.

Reglas:

- `BANK_ACCOUNT` usa proveedor tipo banco.
- `CARD` usa emisor de tarjeta.
- Las monedas permitidas para metodos de pago son `USD` y `GTQ`.
- La interfaz valida que el nombre en tarjeta incluya al menos un nombre y un apellido del usuario autenticado.
- Para cuentas bancarias, el formulario solicita tipo de cuenta y numero completo, pero persiste solo los ultimos 4 digitos.
- Para tarjetas, el formulario solicita numero completo, vencimiento y CVV; numero completo y CVV se validan como datos de entrada y no se persisten.

## Tracking

```text
GET /api/v1/tracking/{remittance_number}
```

El tracking esta protegido. Solo remitente o receptor vinculado pueden consultar la timeline.

## Analitica

```text
GET /api/v1/analytics/summary
GET /api/v1/analytics/remittances-over-time
GET /api/v1/analytics/top-corridors
GET /api/v1/analytics/status-distribution
GET /api/v1/analytics/currency-distribution
GET /api/v1/analytics/method-distribution
```

Los endpoints son de solo lectura y requieren token Bearer con rol `ADMIN` o `RISK_ANALYST`. Un usuario `CLIENT` recibe `403 ANALYTICS_FORBIDDEN`.

La API calcula volumen, comision y ticket promedio como equivalentes USD para agregados globales multimoneda. Las distribuciones por moneda conservan la moneda original.

## Inteligencia de riesgo ML

```text
GET  /api/v1/risk/ml/model-info
GET  /api/v1/risk/ml/metrics
POST /api/v1/risk/ml/predict
```

Los endpoints requieren token Bearer con rol `ADMIN` o `RISK_ANALYST`. Un `CLIENT` recibe `403 RISK_FORBIDDEN`.

`POST /api/v1/risk/ml/predict` recibe:

```json
{
  "features": {
    "account_age_days": 28,
    "transaction_count": 2,
    "source_amount": 980,
    "origin_country": "Estados Unidos",
    "destination_country": "Guatemala"
  }
}
```

El objeto `features` debe incluir todas las variables requeridas por `model_metadata.json`. La respuesta mantiene separadas probabilidad, threshold y clasificacion visual:

```json
{
  "ml_probability": 0.42,
  "model_version": "fraud-model-v1",
  "threshold": 0.25,
  "classification": "MEDIUM",
  "classification_label": "Medio"
}
```

La probabilidad no confirma fraude ni bloquea remesas.

## Corredores bidireccionales

FIDUCIA soporta inicialmente corredores donde Guatemala participa como origen o destino:

```text
Estados Unidos -> Guatemala
Guatemala -> Estados Unidos
Canada -> Guatemala
Guatemala -> Canada
Mexico -> Guatemala
Guatemala -> Mexico
Espana -> Guatemala
Guatemala -> Espana
```

No se permiten corredores como `Estados Unidos -> Canada` durante esta etapa.

## Metodos validos

Pago:

- `DEBIT_CARD`
- `BANK_TRANSFER`
- `DIGITAL_WALLET`

Entrega:

- `BANK_DEPOSIT`
- `TRANSFER`
- `WALLET`
- `CASH_PICKUP`

## Estados internos

```text
CREATED
VALIDATING
RISK_ANALYSIS
APPROVED
PROCESSING
AVAILABLE
COMPLETED
REVIEW_REQUIRED
REJECTED
```

La traduccion amigable se centraliza en frontend.

Para el receptor, `AVAILABLE` significa disponible para recibir, cobrar o retirar segun el metodo de entrega. `COMPLETED` significa recibida o entregada exitosamente.

## Risk Engine Fase 5

Endpoints protegidos para `ADMIN` y `RISK_ANALYST`:

```text
GET  /api/v1/risk/engine-info
GET  /api/v1/risk/dashboard
GET  /api/v1/risk/assessments
GET  /api/v1/risk/assessments/{assessment_id}
GET  /api/v1/risk/remittances/{remittance_id}
POST /api/v1/risk/remittances/{remittance_id}/evaluate
POST /api/v1/risk/assessments/{assessment_id}/review
```

`CLIENT` recibe `403 RISK_FORBIDDEN`. `ESCALATE` y `REJECT` requieren justificacion. El motor no bloquea remesas automaticamente.

## Forecasting Fase 6

Endpoints protegidos para `ADMIN` y `RISK_ANALYST`:

```text
GET /api/v1/forecasting/model-info
GET /api/v1/forecasting/summary
GET /api/v1/forecasting/volume?horizon=4|8|12&granularity=weekly
GET /api/v1/forecasting/amount?horizon=4|8|12&granularity=weekly
GET /api/v1/forecasting/corridors?horizon=4
```

`CLIENT` recibe 403. Horizons, targets y granularidad se validan contra catalogos cerrados.

## Business Intelligence Fase 7

Endpoints protegidos para `ADMIN` y `RISK_ANALYST`:

```text
GET /api/v1/bi/kpis
GET /api/v1/bi/overview
GET /api/v1/bi/trends
GET /api/v1/bi/corridors
GET /api/v1/bi/customers
GET /api/v1/bi/operations
GET /api/v1/bi/risk
GET /api/v1/bi/forecast
GET /api/v1/bi/executive-summary
GET /api/v1/bi/exports/kpis.csv
GET /api/v1/bi/exports/corridors.csv
```

Filtros comunes: `date_from`, `date_to`, `origin_country`, `destination_country`, `currency`, `status`.

`CLIENT` recibe `403 BI_FORBIDDEN`. Las exportaciones CSV son agregadas y no incluyen PII.

## Blockchain y trazabilidad Fase 8

Endpoints protegidos por autenticacion:

```text
GET /api/v1/blockchain/info
GET /api/v1/blockchain/metrics
GET /api/v1/blockchain/overview
GET /api/v1/blockchain/blocks
GET /api/v1/blockchain/blocks/{block_index}
GET /api/v1/blockchain/transactions/{remittance_id}/history
GET /api/v1/blockchain/verify/{remittance_id}
GET /api/v1/blockchain/validate
GET /api/v1/blockchain/integrity/transactions/{remittance_id}
POST /api/v1/blockchain/integrity/verify
GET /api/v1/blockchain/integrity/status
```

Permisos:

- `ADMIN`: consulta de bloques, metricas, historial, verificacion de remesa y validacion completa de cadena.
- `RISK_ANALYST`: consulta de bloques, metricas, historial y verificacion de remesa.
- `CLIENT`: historial y verificacion solo sobre remesas propias; no puede listar ni validar la cadena completa.

Los endpoints devuelven metadatos tecnicos, hashes SHA-256, enlaces entre bloques, nonce, dificultad y estado de validacion. `GET /api/v1/blockchain/overview` entrega en una sola respuesta `info`, `metrics` y `blocks` para consumo de la interfaz web. No devuelven PII, numeros completos de cuentas, tarjetas, documentos, CVV, contrasenas ni tokens.

La validacion de evidencia reconstruye el hash canonico desde la remesa o evaluacion de riesgo operacional y lo compara contra el hash registrado en la cadena local. Si la capa blockchain falla durante una operacion, se registra auditoria y la remesa conserva su flujo transaccional normal.

La verificacion de integridad compara el estado actual de la remesa en BD contra la evidencia criptografica registrada. Puede devolver `VERIFIED`, `INTEGRITY_MISMATCH`, `BLOCKCHAIN_RECORD_MISSING`, `DATABASE_RECORD_MISSING`, `LEGACY_NOT_PROTECTED`, `CHAIN_BROKEN` o `VERIFICATION_ERROR`. Esta dimension no modifica el Risk Engine ni bloquea automaticamente remesas.

Eventos activos registrados por el flujo actual:

- `REMITTANCE_CREATED`
- `REMITTANCE_AVAILABLE`
- `RISK_ASSESSMENT_RECORDED`
- `REMITTANCE_COMPLETED`

`REMITTANCE_CONFIRMED` no se expone como evento activo porque no existe un punto de dominio separado en el lifecycle actual.

## Asistente FIDUCIA Fase 9

Endpoints protegidos por autenticacion:

```text
POST /api/v1/assistant/chat
GET  /api/v1/assistant/conversations
GET  /api/v1/assistant/conversations/{conversation_id}
GET  /api/v1/assistant/capabilities
GET  /api/v1/assistant/info
```

`POST /assistant/chat` recibe:

```json
{
  "conversation_id": null,
  "message": "Cual es el estado de mi ultima remesa?"
}
```

La respuesta incluye `conversation_id`, `message_id`, `answer`, `intent`, `provider`, `tools_used`, `sources`, `source_types`, `warnings` y `generated_at`.

El rol se deriva del token autenticado. El cliente no puede solicitar `role=ADMIN` en el payload. Las conversaciones solo pueden ser leidas por su propietario.

## Sistema Fase 10

```text
GET /health
GET /ready
GET /api/v1/system/info
GET /api/v1/system/metrics
```

`/health` y `/ready` son publicos y responden minimo `status`, `service` y `version`.

`/api/v1/system/info` y `/api/v1/system/metrics` requieren `ADMIN`. Devuelven version de aplicacion, ambiente, estado DB, versiones de componentes y metricas tecnicas simples. No exponen secretos, rutas sensibles ni llaves.

Todas las respuestas HTTP incluyen `X-Request-ID`, `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`.
