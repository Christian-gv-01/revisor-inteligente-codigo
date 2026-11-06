# Evaluación api

Fecha UTC: 2026-11-04T16:54:14.180968+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 19 |
| errores | 1 |
| tasa_completitud | 0.95 |
| latencia_media_ms | 16570.628421052632 |
| latencia_p95_ms | 31847.72 |
| precision_at_k | 0.4509803921568627 |
| recall_at_k | 0.7941176470588235 |
| mrr_at_k | 0.8529411764705882 |
| hit_at_k | 0.8823529411764706 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 17 |
| tp | 11 |
| fp | 0 |
| fn | 0 |
| hallazgos | 11 |
| hallazgos_con_citas_resueltas | 11 |
| referencias | 11 |
| referencias_resueltas | 11 |
| lineas_fuera_rango | 0 |
| precision | 1.0 |
| recall | 1.0 |
| f1 | 1.0 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0.10526315789473684 |
| exactitud_casos_validos | 1 |
| aciertos_sobre_total | 0.95 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 14382.1 |  |
| P02 — SQL interpolado | ok | 21904.22 |  |
| P03 — SQL con formato | ok | 16688.05 |  |
| P04 — Identificador SQL externo | ok | 15581.09 |  |
| P05 — SQL parametrizado | ok | 13920.5 |  |
| P06 — Tabla permitida | ok | 16585.6 |  |
| P07 — os.system externo | error | 7980.16 | HTTP 502 |
| P08 — subprocess shell | ok | 14957.9 |  |
| P09 — os.popen externo | ok | 15869.44 |  |
| P10 — Comando interpolado | ok | 19868.17 |  |
| P11 — Argumentos constantes | ok | 31847.72 |  |
| P12 — Comandos permitidos | ok | 24200.26 |  |
| P13 — eval externo | ok | 15437.86 |  |
| P14 — exec externo | ok | 29682.97 |  |
| P15 — eval en función | ok | 18554.07 |  |
| P16 — eval tras strip | ok | 14008.76 |  |
| P17 — Conversión numérica | ok | 14129.14 |  |
| P18 — Operaciones fijas | ok | 15781.0 |  |
| P19 — Fuera de cobertura: estadística | ok | 744.43 |  |
| P20 — Fuera de cobertura: geometría | ok | 698.66 |  |
