# Evaluación api

Fecha UTC: 2026-11-04T17:35:28.686797+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 17 |
| errores | 3 |
| tasa_completitud | 0.85 |
| latencia_media_ms | 18987.597647058825 |
| latencia_p95_ms | 44428.69 |
| precision_at_k | 0.4666666666666666 |
| recall_at_k | 0.8333333333333334 |
| mrr_at_k | 0.9 |
| hit_at_k | 0.9333333333333333 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 15 |
| tp | 10 |
| fp | 1 |
| fn | 0 |
| hallazgos | 11 |
| hallazgos_con_citas_resueltas | 11 |
| referencias | 11 |
| referencias_resueltas | 11 |
| lineas_fuera_rango | 0 |
| precision | 0.9090909090909091 |
| recall | 1.0 |
| f1 | 0.9523809523809523 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0.11764705882352941 |
| exactitud_casos_validos | 0.9411764705882353 |
| aciertos_sobre_total | 0.8 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 27959.05 |  |
| P02 — SQL interpolado | error | 3512.21 | HTTP 502 |
| P03 — SQL con formato | ok | 6105.01 |  |
| P04 — Identificador SQL externo | ok | 8017.28 |  |
| P05 — SQL parametrizado | error | 3102.29 | HTTP 502 |
| P06 — Tabla permitida | ok | 17729.64 |  |
| P07 — os.system externo | ok | 18483.36 |  |
| P08 — subprocess shell | ok | 19294.22 |  |
| P09 — os.popen externo | ok | 12907.84 |  |
| P10 — Comando interpolado | ok | 14767.35 |  |
| P11 — Argumentos constantes | ok | 39304.28 |  |
| P12 — Comandos permitidos | ok | 7334.05 |  |
| P13 — eval externo | ok | 44428.69 |  |
| P14 — exec externo | error | 14329.27 | HTTP 502 |
| P15 — eval en función | ok | 36307.55 |  |
| P16 — eval tras strip | ok | 17782.29 |  |
| P17 — Conversión numérica | ok | 33198.78 |  |
| P18 — Operaciones fijas | ok | 17838.25 |  |
| P19 — Fuera de cobertura: estadística | ok | 742.9 |  |
| P20 — Fuera de cobertura: geometría | ok | 588.62 |  |
