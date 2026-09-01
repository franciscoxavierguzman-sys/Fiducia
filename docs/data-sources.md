# Fuentes de datos - FIDUCIA Fase 3

## Internas

Las fuentes internas provienen del modelo transaccional de FIDUCIA:

- Usuarios.
- Beneficiarios.
- Metodos de pago.
- Remesas/transacciones.
- Historial de estados.
- Auditoria.
- Catalogos.

La API analitica lee datos operacionales de forma agregada y no expone informacion sensible completa.

## Sinteticas

`scripts/generate_synthetic_data.py` crea datos artificiales reproducibles para investigacion y analitica. Estos datos no se insertan automaticamente en la base operacional.

Comando:

```powershell
.\backend\.venv\Scripts\python.exe scripts\generate_synthetic_data.py --records 10000 --seed 42
```

Salida:

```text
data/synthetic/remittances_synthetic.csv
```

## Externas

Las fuentes externas se incorporaran mediante archivos documentados en `data/external/`. Antes de usar una fuente real debe existir metadata basada en `data/external/metadata-template.json`.

Fuentes priorizadas:

- Banco de Guatemala.
- World Bank.
- IMF.
- Organismos multilaterales.
- Datasets publicos de remesas.
- Datasets publicos de fraude financiero con licencia compatible.

No se descargaron datasets externos en Fase 3.

