# Evaluación A/B del planificador de CODEGUARD

Modelo: `gemini-3.5-flash-lite`. Casos sintéticos: 6.

Solicitudes: 12 · Pares completos: 5 · Pares no comparables: 1.

Cambios observados: 0 · Tasa de cambio: 0.0.

| Caso | Repetición | Sin contexto | Con contexto | Cambio |
|---|---:|---|---|---|
| comando_shell | 1 | detectar_llamadas_sensibles | detectar_llamadas_sensibles | No |
| eval_entrada | 1 | detectar_llamadas_sensibles | detectar_llamadas_sensibles | No |
| exec_entrada | 1 | detectar_llamadas_sensibles | detectar_llamadas_sensibles | No |
| funcion_limpia | 1 | detectar_llamadas_sensibles | detectar_llamadas_sensibles | No |
| sql_concatenado | 1 | revisar_consultas_sql | revisar_consultas_sql | No |

**Limitación:** Un cambio de herramienta NO demuestra mayor precisión ni mejor detección de vulnerabilidades. Se mide una decisión de planificación, sin ejecutar el informe Gemini + RAG. Los errores de proveedor se excluyen de las comparaciones, no son aciertos.
