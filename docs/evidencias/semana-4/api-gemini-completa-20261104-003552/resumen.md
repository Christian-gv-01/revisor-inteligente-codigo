# Evaluación api

Fecha UTC: 2026-11-04T05:35:53.052575+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 3513.4605 |
| latencia_p95_ms | 4626.48 |
| precision_at_k | 0.4629629629629629 |
| recall_at_k | 0.8055555555555556 |
| mrr_at_k | 0.8611111111111112 |
| hit_at_k | 0.8888888888888888 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |
| tp | 12 |
| fp | 1 |
| fn | 0 |
| hallazgos | 13 |
| hallazgos_con_citas_resueltas | 13 |
| referencias | 15 |
| referencias_resueltas | 15 |
| lineas_fuera_rango | 0 |
| precision | 0.9230769230769231 |
| recall | 1.0 |
| f1 | 0.96 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0.1 |
| exactitud_casos_validos | 0.95 |
| aciertos_sobre_total | 0.95 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 4085.95 |  |
| P02 — SQL interpolado | ok | 3993.05 |  |
| P03 — SQL con formato | ok | 4713.16 |  |
| P04 — Identificador SQL externo | ok | 3986.57 |  |
| P05 — SQL parametrizado | ok | 3285.69 |  |
| P06 — Tabla permitida | ok | 3577.09 |  |
| P07 — os.system externo | ok | 4491.38 |  |
| P08 — subprocess shell | ok | 4626.48 |  |
| P09 — os.popen externo | ok | 3677.68 |  |
| P10 — Comando interpolado | ok | 3677.05 |  |
| P11 — Argumentos constantes | ok | 3485.72 |  |
| P12 — Comandos permitidos | ok | 3496.68 |  |
| P13 — eval externo | ok | 3271.06 |  |
| P14 — exec externo | ok | 3486.72 |  |
| P15 — eval en función | ok | 3695.15 |  |
| P16 — eval tras strip | ok | 3474.79 |  |
| P17 — Conversión numérica | ok | 4359.88 |  |
| P18 — Operaciones fijas | ok | 3624.21 |  |
| P19 — Fuera de cobertura: estadística | ok | 658.43 |  |
| P20 — Fuera de cobertura: geometría | ok | 602.47 |  |
