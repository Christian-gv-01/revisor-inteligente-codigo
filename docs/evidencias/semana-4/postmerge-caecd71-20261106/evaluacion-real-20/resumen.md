# Evaluación api

Fecha UTC: 2026-11-06T19:47:41.274708+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 5964.9800000000005 |
| latencia_p95_ms | 8107.56 |
| precision_at_k | 0.4629629629629629 |
| recall_at_k | 0.8055555555555556 |
| mrr_at_k | 0.8611111111111112 |
| hit_at_k | 0.8888888888888888 |
| sin_fuentes_fuera_cobertura | 1.0 |
| casos_con_referencias_esperadas_evaluados | 18 |
| tp | 12 |
| fp | 0 |
| fn | 0 |
| hallazgos | 12 |
| hallazgos_con_citas_resueltas | 12 |
| referencias | 14 |
| referencias_resueltas | 14 |
| lineas_fuera_rango | 0 |
| precision | 1.0 |
| recall | 1.0 |
| f1 | 1.0 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0.1 |
| exactitud_casos_validos | 1 |
| aciertos_sobre_total | 1.0 |
| respuestas_parciales | 0 |
| nota | Errores incluye respuestas parciales; métricas de calidad solo sobre informes completos. No equivale a evaluar el planificador del agente. |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 6585.75 |  |
| P02 — SQL interpolado | ok | 6377.48 |  |
| P03 — SQL con formato | ok | 5168.51 |  |
| P04 — Identificador SQL externo | ok | 6091.18 |  |
| P05 — SQL parametrizado | ok | 6747.14 |  |
| P06 — Tabla permitida | ok | 5093.97 |  |
| P07 — os.system externo | ok | 5365.49 |  |
| P08 — subprocess shell | ok | 7553.93 |  |
| P09 — os.popen externo | ok | 4432.89 |  |
| P10 — Comando interpolado | ok | 6847.16 |  |
| P11 — Argumentos constantes | ok | 8107.56 |  |
| P12 — Comandos permitidos | ok | 4139.34 |  |
| P13 — eval externo | ok | 8403.85 |  |
| P14 — exec externo | ok | 6778.51 |  |
| P15 — eval en función | ok | 5819.69 |  |
| P16 — eval tras strip | ok | 6297.67 |  |
| P17 — Conversión numérica | ok | 5317.91 |  |
| P18 — Operaciones fijas | ok | 5991.94 |  |
| P19 — Fuera de cobertura: estadística | ok | 4549.18 |  |
| P20 — Fuera de cobertura: geometría | ok | 3630.45 |  |
