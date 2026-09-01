# API de FIDUCIA

La API usa el prefijo versionado `/api/v1`.

## Autenticacion

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/users/me
PATCH /api/v1/users/me
```

Los endpoints funcionales de Fase 2 requieren token Bearer.

El registro crea usuarios `CLIENT` y requiere confirmacion de contrasena, aceptacion de terminos, verificacion humana simulada, tipo de documento, numero de documento y fecha de nacimiento. Para `DPI`, el numero debe contener exactamente 13 digitos. Para `PASSPORT`, el numero acepta de 6 a 20 caracteres alfanumericos o guiones.

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
