# Evaluación rag

Fecha UTC: 2026-10-30T20:48:39.887942+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 320.196 |
| latencia_p95_ms | 339.21 |
| precision_at_k | 0.537037037037037 |
| recall_at_k | 0.9444444444444444 |
| mrr_at_k | 0.8888888888888888 |
| hit_at_k | 0.9444444444444444 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 300.71 |  |
| P02 — SQL interpolado | ok | 324.94 |  |
| P03 — SQL con formato | ok | 334.85 |  |
| P04 — Identificador SQL externo | ok | 348.18 |  |
| P05 — SQL parametrizado | ok | 318.87 |  |
| P06 — Tabla permitida | ok | 305.3 |  |
| P07 — os.system externo | ok | 320.52 |  |
| P08 — subprocess shell | ok | 320.2 |  |
| P09 — os.popen externo | ok | 302.28 |  |
| P10 — Comando interpolado | ok | 314.76 |  |
| P11 — Argumentos constantes | ok | 324.51 |  |
| P12 — Comandos permitidos | ok | 302.0 |  |
| P13 — eval externo | ok | 304.86 |  |
| P14 — exec externo | ok | 339.21 |  |
| P15 — eval en función | ok | 318.73 |  |
| P16 — eval tras strip | ok | 328.34 |  |
| P17 — Conversión numérica | ok | 324.61 |  |
| P18 — Operaciones fijas | ok | 335.41 |  |
| P19 — Fuera de cobertura: estadística | ok | 334.64 |  |
| P20 — Fuera de cobertura: geometría | ok | 301.0 |  |
