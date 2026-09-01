# Evaluacion De Forecasting

## Modelo Seleccionado

Para ambos targets se selecciono `Moving Average 8` usando validation.

## Validation

| Target | Modelo | MAE | RMSE | WAPE | sMAPE |
| --- | --- | ---: | ---: | ---: | ---: |
| transaction_count | Moving Average 8 | 7.5729 | 9.1095 | 0.0603 | 0.0594 |
| transaction_amount_usd | Moving Average 8 | 1511.8941 | 1781.0709 | 0.0594 | 0.0597 |

## Test

| Target | Modelo | MAE | RMSE | WAPE | sMAPE |
| --- | --- | ---: | ---: | ---: | ---: |
| transaction_count | Moving Average 8 | 13.8854 | 19.6157 | 0.1098 | 0.1153 |
| transaction_amount_usd | Moving Average 8 | 4022.9019 | 4961.8058 | 0.1627 | 0.1666 |

## Comparacion

El candidato `HistGradientBoosting` obtuvo mejor test en monto, pero no fue seleccionado porque validation favorecio `Moving Average 8` y la seleccion no debe basarse en test.

Reportes completos:

- `reports/forecasting/model_comparison.json`
- `reports/forecasting/backtest_results.json`

## Drift

Indicador actual: `NORMAL`, porque WAPE test se mantiene bajo los umbrales descriptivos iniciales.
