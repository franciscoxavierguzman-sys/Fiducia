# Fase 2 - Remesas

## Objetivo

Implementar el flujo funcional principal de remesas simuladas bidireccionales con Guatemala como mercado central:

```text
Login
-> Dashboard cliente
-> Crear beneficiario
-> Nueva remesa
-> Simular costos
-> Confirmar operacion
-> Crear transaccion
-> Remesa disponible
-> Beneficiario consulta remesas recibidas
-> Beneficiario recibe o cobra remesa
-> Transaccion completada
-> Historial
-> Detalle
-> Logout
```

## Funcionalidades implementadas

- Gestion basica de beneficiarios propios.
- Cotizacion de remesas hacia Guatemala.
- Cotizacion de remesas bidireccionales `Mundo -> Guatemala` y `Guatemala -> Mundo`.
- Metodos de pago ficticios.
- Tracking protegido por numero de remesa.
- Perfil editable.
- Registro visible desde frontend.
- Corredores configurables en `remittance_corridors`.
- Calculo de comision desde configuracion.
- Tipo de cambio simulado desde tabla `exchange_rates`.
- Creacion de transacciones simuladas.
- Historial de remesas enviadas ordenado por fecha descendente.
- Vista de remesas recibidas para beneficiarios con cuenta vinculada.
- Accion controlada para recibir, cobrar o confirmar recepcion de una remesa disponible.
- Detalle de transaccion.
- Dashboard cliente basico.
- Auditoria de beneficiarios, transacciones y recepcion.
- Proteccion de endpoints con JWT.
- Control de acceso por usuario autenticado.
- Vinculacion opcional de beneficiario con usuario FIDUCIA por correo.

## Formulas

```text
commission_amount = amount * commission_rate
total_amount = amount + commission_amount
destination_amount = amount * exchange_rate
```

Supuesto de esta fase:

```text
Monto enviado = monto que recibe conversion
Comision = costo adicional
Costo total = monto enviado + comision
Monto destino = monto enviado * tipo de cambio
```

Ejemplo validado:

```text
USD 400.00 * 2.25 % = USD 9.00
USD 400.00 + USD 9.00 = USD 409.00
USD 400.00 * 7.80 = GTQ 3,120.00
```

## Supuestos simulados

- El tipo de cambio inicial es simulado.
- Guatemala debe participar como origen o destino durante esta etapa.
- No se permiten todavia corredores Mundo -> Mundo, por ejemplo Estados Unidos -> Canada.
- Los metodos de pago y entrega son simulados.
- No se procesan tarjetas, pagos ni integraciones bancarias reales.
- Recibir o cobrar una remesa solo persiste el cambio de estado en el prototipo.
- No se implementa todavia scoring ML ni riesgo hibrido.

## Validaciones ejecutadas

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

Resultado:

```text
27 passed
```

```bash
cd frontend
npm run build
```

Resultado:

```text
✓ built
```

## Validacion viva del flujo

Se levanto temporalmente la API actualizada en `http://127.0.0.1:8010` y se ejecuto:

```text
Registro
Login
Crear beneficiario
Simular USD 400
Crear transaccion
Consultar historial
Abrir detalle
```

Resultado:

```text
Commission: 9.00
Total: 409.00
Exchange: 7.800000
Destination: 3120.00
Transaction: FID-2026-000001
Status: AVAILABLE
HistoryCount: 1
```

## Ajuste bidireccional validado

Se agregaron y validaron los escenarios:

```text
Estados Unidos -> Guatemala
USD 400.00 -> GTQ 3,120.00
Comision: USD 9.00
```

```text
Guatemala -> Estados Unidos
GTQ 3,000.00 -> USD 384.62
Comision: GTQ 67.50
```

Tambien se cubren por pruebas:

- rechazo de `Estados Unidos -> Canada`;
- rechazo de `Guatemala -> Guatemala`;
- rechazo de beneficiario incompatible con pais destino.

## Ajuste de recepcion validado

Se agrego el punto de vista del beneficiario receptor:

```text
Usuario A envia remesa
Transaccion queda AVAILABLE
Usuario B, vinculado como beneficiario, abre Remesas recibidas
Usuario B confirma recepcion/cobro
Transaccion pasa a COMPLETED
Usuario A tambien observa COMPLETED en Remesas enviadas
```

Reglas cubiertas:

- beneficiario registrado puede visualizar remesa asociada;
- beneficiario sin cuenta no ve la remesa hasta vincularse;
- usuario diferente no puede consultar ni recibir remesas ajenas;
- no se puede recibir una remesa en `CREATED`, `VALIDATING` o `PROCESSING`;
- no se permite doble cobro cuando ya esta `COMPLETED`;
- la recepcion queda auditada con estado anterior y nuevo.

## Criterios de aceptacion

- Usuario puede autenticarse: cumplido.
- Puede crear beneficiario: cumplido.
- Puede agregar metodo de pago: cumplido.
- Puede actualizar perfil: cumplido.
- Puede consultar beneficiarios: cumplido.
- Puede iniciar nueva remesa: cumplido.
- Puede obtener cotizacion real desde backend: cumplido.
- Puede cotizar Estados Unidos -> Guatemala: cumplido.
- Puede cotizar Guatemala -> Estados Unidos: cumplido.
- Comision correcta: cumplido.
- Tipo de cambio aplicado correctamente: cumplido.
- Puede confirmar operacion: cumplido.
- Transaccion persistida: cumplido.
- Puede consultar remesas enviadas: cumplido.
- Puede consultar remesas recibidas: cumplido.
- Puede rastrear una remesa por numero FID: cumplido.
- Puede completar recepcion `AVAILABLE -> COMPLETED`: cumplido.
- Puede abrir detalle: cumplido.
- No accede a datos de otros usuarios: cubierto por pruebas.
- Calculos usan Decimal: cumplido.
- Valores historicos quedan congelados: cubierto por pruebas.
- Documentacion actualizada: cumplido.
- Puede demostrar enviar + recibir + completar entre dos usuarios: cumplido por backend y disponible en frontend.

## Preparacion para Fase 3

Quedaron preparados:

- estructura `data/`;
- transacciones persistidas;
- beneficiarios y paises;
- tabla de tipos de cambio;
- auditoria basica.

Datos necesarios para Fase 3:

- generador sintetico ampliado;
- volumen de transacciones mayor;
- metadatos de patrones anomalos;
- datasets externos documentados si se incorporan.
