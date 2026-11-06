# Evaluación api

Fecha UTC: 2026-11-04T18:03:18.472152+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 20 |
| completados | 20 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 21450.1375 |
| latencia_p95_ms | 37074.06 |
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
| referencias | 13 |
| referencias_resueltas | 13 |
| lineas_fuera_rango | 0 |
| precision | 1.0 |
| recall | 1.0 |
| f1 | 1.0 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0.1 |
| exactitud_casos_validos | 1 |
| aciertos_sobre_total | 1.0 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 18007.52 |  |
| P02 — SQL interpolado | ok | 22936.35 |  |
| P03 — SQL con formato | ok | 11981.55 |  |
| P04 — Identificador SQL externo | ok | 16901.7 |  |
| P05 — SQL parametrizado | ok | 32962.65 |  |
| P06 — Tabla permitida | ok | 19388.03 |  |
| P07 — os.system externo | ok | 22995.17 |  |
| P08 — subprocess shell | ok | 47018.87 |  |
| P09 — os.popen externo | ok | 24781.0 |  |
| P10 — Comando interpolado | ok | 23357.16 |  |
| P11 — Argumentos constantes | ok | 12792.23 |  |
| P12 — Comandos permitidos | ok | 30835.68 |  |
| P13 — eval externo | ok | 19233.76 |  |
| P14 — exec externo | ok | 37074.06 |  |
| P15 — eval en función | ok | 26612.55 |  |
| P16 — eval tras strip | ok | 20754.21 |  |
| P17 — Conversión numérica | ok | 18875.67 |  |
| P18 — Operaciones fijas | ok | 21223.69 |  |
| P19 — Fuera de cobertura: estadística | ok | 645.24 |  |
| P20 — Fuera de cobertura: geometría | ok | 625.66 |  |
