# Ciclo de vida de remesa - FIDUCIA

## Flujo principal

```text
Registro
-> Login
-> Perfil
-> Metodo de pago
-> Beneficiario
-> Nueva remesa
-> Cotizacion
-> Confirmacion
-> Remesa disponible
-> Tracking
-> Recepcion / cobro
-> Completada
```

## Registro y usuario

El usuario se registra como `CLIENT`. La clasificacion como remitente o receptor depende de su participacion en una remesa:

- `sender_id`: usuario que envia.
- `beneficiary_user_id`: usuario que recibe, cuando el beneficiario esta vinculado.

El registro requiere correo unico, telefono valido, contrasena con letras y numeros, confirmacion de contrasena y aceptacion de terminos del prototipo.

## Beneficiario y vinculacion

La estrategia seleccionada para el prototipo es vinculacion por correo. Si el correo del beneficiario coincide con una cuenta existente, se guarda `beneficiary_user_id`. Si no coincide, la remesa puede enviarse igualmente, pero no aparece en `Remesas recibidas` hasta que el beneficiario quede vinculado.

## Funding, fee y FX

Los metodos de pago se guardan en `funding_sources` con datos ficticios y ultimos cuatro digitos.

```text
commission_amount = source_amount * commission_rate
total_debit_amount = source_amount + commission_amount
destination_amount = source_amount * exchange_rate
```

La comision se cobra en moneda origen. El tipo de cambio, comision y total debitado quedan congelados en la remesa.

## Numero y tracking

Cada remesa tiene `remittance_uuid` interno y `remittance_number` publico, por ejemplo `FID-2026-000001`. El tracking por numero esta protegido para remitente o receptor vinculado.

## Estados

En la consolidacion actual, al confirmar una remesa queda `AVAILABLE` para demostrar el ciclo completo sin implementar todavia Risk Engine. Al recibir o cobrar pasa a `COMPLETED`.

Cada cambio se registra en `remittance_status_history`.

## Seguridad

- El remitente solo ve sus remesas enviadas.
- El receptor solo ve remesas donde `beneficiary_user_id` coincide con su usuario.
- Un tercero no puede consultar ni recibir una remesa ajena aunque conozca el numero FID.
- El frontend no modifica estados directamente.

FIDUCIA representa el flujo de una plataforma de remesas, pero no procesa dinero real ni integra servicios financieros reales en esta etapa.
