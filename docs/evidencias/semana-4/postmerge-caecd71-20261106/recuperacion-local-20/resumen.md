# Evaluación rag

Fecha UTC: 2026-11-06T19:47:53.001798+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 163.879 |
| latencia_p95_ms | 182.95 |
| precision_at_k | 0.4629629629629629 |
| recall_at_k | 0.8055555555555556 |
| mrr_at_k | 0.8611111111111112 |
| hit_at_k | 0.8888888888888888 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 175.91 |  |
| P02 — SQL interpolado | ok | 180.61 |  |
| P03 — SQL con formato | ok | 151.24 |  |
| P04 — Identificador SQL externo | ok | 153.56 |  |
| P05 — SQL parametrizado | ok | 182.09 |  |
| P06 — Tabla permitida | ok | 151.43 |  |
| P07 — os.system externo | ok | 152.67 |  |
| P08 — subprocess shell | ok | 156.06 |  |
| P09 — os.popen externo | ok | 153.72 |  |
| P10 — Comando interpolado | ok | 150.29 |  |
| P11 — Argumentos constantes | ok | 151.6 |  |
| P12 — Comandos permitidos | ok | 182.95 |  |
| P13 — eval externo | ok | 180.35 |  |
| P14 — exec externo | ok | 184.88 |  |
| P15 — eval en función | ok | 180.87 |  |
| P16 — eval tras strip | ok | 151.41 |  |
| P17 — Conversión numérica | ok | 152.98 |  |
| P18 — Operaciones fijas | ok | 165.03 |  |
| P19 — Fuera de cobertura: estadística | ok | 161.91 |  |
| P20 — Fuera de cobertura: geometría | ok | 158.02 |  |
