# Metodologia De Forecasting

Version: `remittance-forecast-v1`.

## Dataset

Fuente: `data/processed/remittances_analytics.csv`.

Dataset preparado: `data/processed/forecasting/weekly_remittances_forecasting.csv`.

Los montos se convierten a `USD equivalent` usando tasas analiticas constantes para evitar sumar monedas diferentes.

## Targets

- `transaction_count`: cantidad semanal de remesas.
- `transaction_amount_usd`: monto semanal agregado en USD equivalente.

## Validacion Temporal

No se usa random split. La particion respeta orden temporal:

- Train: 2025-03-03 a 2026-03-09.
- Validation: 2026-03-16 a 2026-06-01.
- Test: 2026-06-08 a 2026-08-24.

## Walk-Forward

La evaluacion simula entrenar con pasado, pronosticar el siguiente periodo, observar actual y avanzar.

## Leakage

No se usan features futuras. Los modelos basados en lags/moving average calculan predicciones solo con historia disponible antes del periodo pronosticado.

## Intervalos

Los intervalos 80% y 95% se estiman con cuantiles absolutos de residuales sobre validation. Son rangos experimentales, no garantias.
