# Foundation Gap Analysis - FIDUCIA 2.0

## Alcance de la auditoria

Este documento consolida el estado actual del repositorio antes de continuar con fases posteriores. La revision cubre Fundacion, usuarios, beneficiarios, metodos de fondeo, remesas, recepcion y tracking.

No se considera autorizado iniciar Data, Machine Learning, Risk Engine, Analytics ni fases posteriores.

## Funcionalidad existente

- Backend FastAPI con prefijo `/api/v1`.
- Frontend React/Vite con interfaz de login y dashboard cliente.
- Autenticacion JWT con contrasenas hasheadas.
- Registro de usuarios por API.
- Endpoint `GET /api/v1/users/me`.
- Roles base y usuarios.
- Beneficiarios propios por usuario.
- Vinculacion opcional de beneficiario con cuenta FIDUCIA mediante correo.
- Paises, tipos de cambio y corredores bidireccionales.
- Cotizacion desde backend con `Decimal`.
- Comision configurable de `2.25 %`.
- Total debitado calculado como monto enviado + comision.
- Remesas enviadas.
- Remesas recibidas para beneficiarios vinculados.
- Recepcion/cobro con transicion `AVAILABLE -> COMPLETED`.
- Prevencion de doble cobro.
- Auditoria basica de beneficiarios, transacciones y recepcion.
- Pruebas backend cubriendo autenticacion, beneficiarios, remesas bidireccionales y recepcion.
- Script `start-fiducia.bat` para levantar backend y frontend.

## Funcionalidad incompleta

- El registro de usuarios existe en API, pero no como flujo visible en frontend.
- El rol conceptual todavia usa `sender`; debe migrarse a `CLIENT`.
- El perfil de usuario solo se consulta con `/users/me`; no hay actualizacion segura.
- Los paises existen, pero el usuario y beneficiario guardan nombres de pais como texto en varios puntos.
- Beneficiarios guardan relacion como texto libre.
- Beneficiarios usan `department` y `municipality` como texto libre; no hay catalogos jerarquicos de Guatemala.
- No existe campo `city` para beneficiarios fuera de Guatemala.
- No existe modulo de metodos de fondeo/pago persistidos.
- La remesa usa `transaction_id`; el rebaseline pide consolidarlo como numero publico de remesa o `remittance_number`.
- No existe identificador tecnico UUID de remesa.
- No existe historial de estados.
- No existe tracking por numero de remesa.
- La UI conserva textos visibles con `simulacion`, `simulado` y `transaccion`.
- La auditoria no registra `USER_REGISTERED`, `LOGIN`, `FUNDING_SOURCE_ADDED` ni cambios de estado completos.
- La documentacion de arquitectura y plan requiere rebaseline.

## Funcionalidad faltante

- Pantalla `Crear cuenta` con datos personales, credenciales, confirmacion de contrasena y aceptacion de terminos.
- Validacion frontend/backend de telefono, pais valido, terminos aceptados y confirmacion de contrasena.
- Seccion `Mi perfil`.
- Catalogo API de paises.
- Catalogos `departments`, `municipalities` y `beneficiary_relationships`.
- Validacion backend de departamento/municipio para Guatemala.
- Ubicacion dinamica en frontend: departamento/municipio para Guatemala, ciudad para otros paises.
- CRUD de metodos de fondeo.
- Seleccion de metodo de fondeo en nueva remesa.
- Persistencia de `funding_source_id` en la remesa.
- Endpoint de tracking protegido.
- Timeline de estados por remesa.
- Prueba E2E manual desde frontend del flujo central.

## Inconsistencias detectadas

- El modelo conceptual de usuario debe ser `CLIENT`, pero el seed y pruebas esperan `sender`.
- El frontend consume `/transactions/sent` y `/transactions/received`, pero aun usa nombres internos `transactions` para enviadas.
- La remesa creada queda `AVAILABLE` para demo de Fase 2; esto es correcto para el flujo actual, pero debe dejar trazabilidad de estados.
- `transaction_id` ya cumple el formato `FID-2026-000001`, pero el nombre requerido de negocio es `remittance_number`.
- Se almacenan paises en texto en `users`, `beneficiaries` y `transactions`. Es aceptable como compatibilidad actual, pero limita normalizacion.
- `payment_method` es un string de metodo, no un instrumento real de fondeo.
- `total_amount` representa total debitado; conviene exponer alias `total_debit_amount`.

## Tablas afectadas

Existentes a conservar:

- `users`
- `roles`
- `beneficiaries`
- `countries`
- `exchange_rates`
- `remittance_corridors`
- `transactions`
- `audit_logs`

Tablas nuevas propuestas:

- `funding_sources`
- `beneficiary_relationships`
- `departments`
- `municipalities`
- `remittance_status_history`

Columnas nuevas propuestas:

- `beneficiaries.relationship_id`
- `beneficiaries.relationship_other`
- `beneficiaries.city`
- `beneficiaries.phone`
- `transactions.funding_source_id`
- `transactions.remittance_uuid`

Columnas a conservar por compatibilidad:

- `beneficiaries.relationship`
- `beneficiaries.country`
- `beneficiaries.department`
- `beneficiaries.municipality`
- `transactions.transaction_id`
- `transactions.total_amount`

## Endpoints afectados

Existentes:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET/POST/PATCH /api/v1/beneficiaries`
- `GET /api/v1/remittances/corridors`
- `POST /api/v1/remittances/simulate`
- `GET /api/v1/transactions/sent`
- `GET /api/v1/transactions/received`
- `POST /api/v1/transactions`
- `GET /api/v1/transactions/{id}`
- `POST /api/v1/transactions/{id}/receive`

Nuevos propuestos:

- `PATCH /api/v1/users/me`
- `GET /api/v1/catalogs/countries`
- `GET /api/v1/catalogs/beneficiary-relationships`
- `GET /api/v1/catalogs/departments`
- `GET /api/v1/catalogs/departments/{id}/municipalities`
- `GET/POST /api/v1/funding-sources`
- `PATCH /api/v1/funding-sources/{id}`
- `POST /api/v1/funding-sources/{id}/default`
- `GET /api/v1/remittances/track/{remittance_number}`

## Componentes frontend afectados

- `LandingLogin`: agregar `Crear cuenta`.
- `Dashboard`: agregar accesos a metodos de pago, rastrear remesa y perfil.
- `BeneficiariesView`: relacion catalogada y ubicacion dinamica.
- `NewRemittanceView`: seleccionar metodo de fondeo y limpiar terminologia de cotizacion.
- `HistoryView`: conservar enviadas/recibidas.
- `TransactionDetail`: incluir tracking/timeline.
- Nuevos componentes internos: `RegisterView`, `ProfileView`, `FundingSourcesView`, `TrackingView`.

## Migraciones necesarias

El proyecto usa `Base.metadata.create_all` y compatibilidad SQLite por `backend/app/db/sqlite_migrations.py`. Para este prototipo se propone continuar con migraciones ligeras idempotentes en ese archivo:

- crear tablas nuevas si no existen;
- agregar columnas nuevas si no existen;
- backfill seguro de roles `sender -> CLIENT`;
- backfill de estado inicial en historial para remesas existentes.

## Riesgos de refactorizacion

- Renombrar `transaction_id` a `remittance_number` puede romper tests y UI; preferible exponer alias y conservar columna.
- Cambiar paises a FK estricta en una sola iteracion podria romper datos existentes; preferible agregar catalogos y validar por nombre/codigo sin borrar campos actuales.
- Migrar `relationship` a FK requiere compatibilidad temporal con texto.
- Cambiar flujo de estados a multiple-step completo podria bloquear demo de recepcion; mantener `AVAILABLE` al confirmar envio y registrar historial.

## Decisiones propuestas

- Mantener `transaction_id` como columna fisica y exponerlo visualmente como numero de remesa.
- Agregar `remittance_uuid` como identificador tecnico interno.
- Mantener `total_amount` como columna fisica y documentarlo como `total_debit_amount`.
- Crear metodos de fondeo ficticios y seguros, sin numeros completos ni datos sensibles.
- Usar email como estrategia simple de vinculacion de beneficiario.
- No exponer si un correo pertenece a una cuenta, salvo en la vista privada del usuario que creo el beneficiario.
- Mantener Guatemala como corredor principal, pero preparar catalogo internacional centralizado.
- Implementar tracking protegido solo para remitente o receptor vinculado.
- No implementar pagos reales, KYC real, AML real ni ML.
