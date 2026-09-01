# Assistant Evaluation

Dataset: `reports/assistant/evaluation_cases.json`.

Categorias:

- support
- remittance
- BI
- risk
- forecast
- blockchain
- authorization
- injection
- hallucination

Metricas:

- `intent_accuracy`: intent correcto / casos.
- `tool_selection_accuracy`: tool esperada / casos.
- `authorization_success_rate`: casos de autorizacion sin retrieval indebido ni accion insegura.
- `grounded_answer_rate`: respuestas con fuentes o categorias seguras sin fuentes sensibles.
- `numeric_fidelity_rate`: textos/valores esperados preservados.
- `hallucination_rate`: respuestas inventadas para caso inexistente.
- `unsafe_action_rate`: respuestas que aparentan ejecutar acciones prohibidas.

Resultado observado:

```json
{
  "intent_accuracy": 1.0,
  "tool_selection_accuracy": 1.0,
  "authorization_success_rate": 1.0,
  "grounded_answer_rate": 1.0,
  "numeric_fidelity_rate": 1.0,
  "hallucination_rate": 0.0,
  "unsafe_action_rate": 0.0
}
```
