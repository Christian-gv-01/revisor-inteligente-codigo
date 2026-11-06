# Evaluación rag

Fecha UTC: 2026-11-04T00:21:13.158456+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 679.452 |
| latencia_p95_ms | 795.42 |
| precision_at_k | 0.4629629629629629 |
| recall_at_k | 0.8055555555555556 |
| mrr_at_k | 0.8611111111111112 |
| hit_at_k | 0.8888888888888888 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 651.67 |  |
| P02 — SQL interpolado | ok | 617.66 |  |
| P03 — SQL con formato | ok | 616.33 |  |
| P04 — Identificador SQL externo | ok | 636.91 |  |
| P05 — SQL parametrizado | ok | 695.91 |  |
| P06 — Tabla permitida | ok | 687.99 |  |
| P07 — os.system externo | ok | 665.88 |  |
| P08 — subprocess shell | ok | 671.53 |  |
| P09 — os.popen externo | ok | 677.96 |  |
| P10 — Comando interpolado | ok | 726.52 |  |
| P11 — Argumentos constantes | ok | 675.21 |  |
| P12 — Comandos permitidos | ok | 827.49 |  |
| P13 — eval externo | ok | 795.42 |  |
| P14 — exec externo | ok | 682.22 |  |
| P15 — eval en función | ok | 645.44 |  |
| P16 — eval tras strip | ok | 651.05 |  |
| P17 — Conversión numérica | ok | 686.42 |  |
| P18 — Operaciones fijas | ok | 677.98 |  |
| P19 — Fuera de cobertura: estadística | ok | 624.68 |  |
| P20 — Fuera de cobertura: geometría | ok | 674.77 |  |
