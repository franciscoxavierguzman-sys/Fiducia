# FIDUCIA Fase 3 - Plan de datos y analitica

## Alcance

La Fase 3 construye una capa analitica separada de la operacion transaccional de FIDUCIA. El objetivo es producir datos sinteticos reproducibles, validarlos, transformarlos en un dataset analitico y exponer analitica descriptiva basica sin entrenar modelos de Machine Learning ni activar un Risk Engine definitivo.

## Fuentes internas

- `users`: perfil, pais, fecha de registro, rol y estado activo. No se extraen contrasenas ni credenciales.
- `funding_sources`: tipo de metodo de pago, proveedor, moneda, estado activo y ultimos cuatro digitos. No se almacenan ni exportan numeros completos, CVV o PIN.
- `beneficiaries`: relacion, pais destino, moneda, metodo de entrega, indicador de usuario vinculado y antiguedad.
- `transactions`: remesas, corredor, montos, comisiones, tipo de cambio, estados y fechas.
- `remittance_status_history`: timeline de estados para analitica futura de tiempos operativos.
- `audit_logs`: eventos operativos agregables sin exponer secretos.
- Catalogos: paises, monedas, corredores, relaciones, departamentos y municipios.

## Datos sinteticos necesarios

El generador `scripts/generate_synthetic_data.py` produce remesas sinteticas compatibles con el modelo conceptual:

`User -> Funding Source -> Beneficiary -> Remittance -> Fee -> FX -> Payout -> Tracking -> Receipt`

Los registros incluyen:

- Usuarios anonimizados.
- Corredores internacionales con presencia relevante de Guatemala.
- Monedas coherentes por pais.
- Montos, comisiones, debitos, tipo de cambio y monto destino calculados con `Decimal`.
- Variables de comportamiento como velocidad transaccional, diversidad de paises, montos historicos y horario.
- Etiqueta `fraud_label` sintetica para investigacion futura.

Los datos no se insertan automaticamente en SQLite operacional.

## Datasets externos previstos

La arquitectura reserva `data/external/` para fuentes publicas documentadas. Fuentes priorizadas:

- Banco de Guatemala.
- World Bank.
- IMF.
- Organismos multilaterales.
- Datasets publicos de remesas.
- Datasets publicos de fraude financiero con licencia compatible.

Cada fuente externa debe registrarse con metadata antes de incorporarse al pipeline.

## Esquema analitico

El dataset final se genera en `data/processed/remittances_analytics.csv`. Sus variables se documentan en `docs/data-dictionary.md`.

Categorias:

- Identificadores sinteticos y anonimizados.
- Atributos de usuario.
- Atributos de beneficiario.
- Atributos transaccionales.
- Calculos monetarios.
- Features de comportamiento.
- Variables experimentales para riesgo futuro.
- Etiquetas sinteticas de fraude.

## Transformaciones

1. Extraccion desde `data/synthetic/remittances_synthetic.csv`.
2. Validacion de estructura, paises, monedas, montos, comisiones, fechas, estados y duplicados.
3. Limpieza de tipos y normalizacion textual.
4. Feature engineering base.
5. Exportacion de dataset procesado.
6. Emision de reporte de calidad en `data/processed/validation_report.json`.

## Calidad de datos

Las validaciones detectan:

- IDs duplicados.
- Campos obligatorios nulos.
- Montos negativos.
- Monedas invalidas.
- Paises inexistentes.
- Origen igual a destino.
- Fechas inconsistentes.
- Tipo de cambio menor o igual a cero.
- Comision, total debitado y monto destino incorrectos.
- Estados fuera del catalogo.

## Estrategia para ML futuro

La Fase 3 deja variables listas para analisis, pero no entrena modelos. Los campos `rule_score`, `ml_probability`, `anomaly_score`, `final_risk_score` y `fraud_label` deben tratarse como experimentales o preparados para investigacion, nunca como decisiones reales de riesgo.

La Fase 4 podra usar este dataset para evaluar modelos supervisados o no supervisados, siempre documentando metricas, sesgos, limites y trazabilidad.
