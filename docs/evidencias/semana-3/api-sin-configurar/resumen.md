# Evaluación api

Fecha UTC: 2026-10-30T21:03:33.344652+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 0 |
| errores | 20 |
| tasa_completitud | 0.0 |
| latencia_media_ms | No disponible |
| latencia_p95_ms | No disponible |
| precision_at_k | No disponible |
| recall_at_k | No disponible |
| mrr_at_k | No disponible |
| hit_at_k | No disponible |
| sin_fuentes_fuera_cobertura | No disponible |
| casos_con_referencias_esperadas_evaluados | 0 |
| tp | 0 |
| fp | 0 |
| fn | 0 |
| hallazgos | 0 |
| hallazgos_con_citas_resueltas | 0 |
| referencias | 0 |
| referencias_resueltas | 0 |
| lineas_fuera_rango | 0 |
| precision | No disponible |
| recall | No disponible |
| f1 | No disponible |
| cobertura_citas | No disponible |
| validez_referencias | No disponible |
| tasa_abstencion | No disponible |
| exactitud_casos_validos | No disponible |
| aciertos_sobre_total | 0.0 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | error | 97.07 | HTTP 503 |
| P02 — SQL interpolado | error | 3.9 | HTTP 503 |
| P03 — SQL con formato | error | 3.51 | HTTP 503 |
| P04 — Identificador SQL externo | error | 3.17 | HTTP 503 |
| P05 — SQL parametrizado | error | 3.49 | HTTP 503 |
| P06 — Tabla permitida | error | 2.94 | HTTP 503 |
| P07 — os.system externo | error | 26.14 | HTTP 503 |
| P08 — subprocess shell | error | 3.6 | HTTP 503 |
| P09 — os.popen externo | error | 3.08 | HTTP 503 |
| P10 — Comando interpolado | error | 4.03 | HTTP 503 |
| P11 — Argumentos constantes | error | 5.15 | HTTP 503 |
| P12 — Comandos permitidos | error | 3.46 | HTTP 503 |
| P13 — eval externo | error | 3.75 | HTTP 503 |
| P14 — exec externo | error | 2.23 | HTTP 503 |
| P15 — eval en función | error | 20.84 | HTTP 503 |
| P16 — eval tras strip | error | 4.11 | HTTP 503 |
| P17 — Conversión numérica | error | 4.93 | HTTP 503 |
| P18 — Operaciones fijas | error | 4.76 | HTTP 503 |
| P19 — Fuera de cobertura: estadística | error | 3.84 | HTTP 503 |
| P20 — Fuera de cobertura: geometría | error | 2.94 | HTTP 503 |
