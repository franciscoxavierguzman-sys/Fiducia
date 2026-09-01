# Pipeline de datos - FIDUCIA Fase 3

## Flujo

```text
Generate synthetic
  -> Extract CSV
  -> Validate
  -> Clean
  -> Feature engineering
  -> Export processed CSV
  -> Descriptive analytics
```

## Ejecutar pipeline

Desde la raiz:

```powershell
.\backend\.venv\Scripts\python.exe scripts\data_pipeline.py --records 10000 --seed 42
```

Salidas:

- `data/synthetic/remittances_synthetic.csv`
- `data/processed/remittances_analytics.csv`
- `data/processed/validation_report.json`

## Analitica descriptiva sobre CSV procesado

```powershell
.\backend\.venv\Scripts\python.exe scripts\descriptive_analytics.py
```

Salida:

- `data/processed/descriptive_summary.json`

## Validaciones

El pipeline valida IDs duplicados, campos obligatorios, monedas, paises, origen distinto de destino, estados, metodos, montos negativos, tipo de cambio, comision, total debitado, monto destino y consistencia de fechas.

## Precision monetaria

Los calculos financieros usan `Decimal` y redondeo explicito a dos decimales para dinero y seis decimales para tasas.

## Limites

La Fase 3 no entrena modelos, no publica predicciones reales y no ejecuta procesos de pago. Los puntajes y etiquetas son sinteticos para investigacion futura.
