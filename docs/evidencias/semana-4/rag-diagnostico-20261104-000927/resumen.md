# Evaluación rag

Fecha UTC: 2026-11-04T05:09:28.129564+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 690.9014999999999 |
| latencia_p95_ms | 805.53 |
| precision_at_k | 0.4629629629629629 |
| recall_at_k | 0.8055555555555556 |
| mrr_at_k | 0.8611111111111112 |
| hit_at_k | 0.8888888888888888 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 620.58 |  |
| P02 — SQL interpolado | ok | 619.73 |  |
| P03 — SQL con formato | ok | 626.22 |  |
| P04 — Identificador SQL externo | ok | 689.66 |  |
| P05 — SQL parametrizado | ok | 811.54 |  |
| P06 — Tabla permitida | ok | 648.25 |  |
| P07 — os.system externo | ok | 805.53 |  |
| P08 — subprocess shell | ok | 732.93 |  |
| P09 — os.popen externo | ok | 670.89 |  |
| P10 — Comando interpolado | ok | 677.34 |  |
| P11 — Argumentos constantes | ok | 726.43 |  |
| P12 — Comandos permitidos | ok | 713.96 |  |
| P13 — eval externo | ok | 679.89 |  |
| P14 — exec externo | ok | 698.85 |  |
| P15 — eval en función | ok | 678.59 |  |
| P16 — eval tras strip | ok | 658.21 |  |
| P17 — Conversión numérica | ok | 673.37 |  |
| P18 — Operaciones fijas | ok | 690.8 |  |
| P19 — Fuera de cobertura: estadística | ok | 705.43 |  |
| P20 — Fuera de cobertura: geometría | ok | 689.83 |  |
