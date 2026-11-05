# Evaluación rag

Fecha UTC: 2026-11-04T22:21:31.248985+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 25 |
| completados | 25 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 648.3544 |
| latencia_p95_ms | 829.04 |
| precision_at_k | 0.44 |
| recall_at_k | 0.92 |
| mrr_at_k | 0.96 |
| hit_at_k | 0.96 |
| sin_fuentes_fuera_cobertura | No disponible |
| casos_con_referencias_esperadas_evaluados | 25 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 644.65 |  |
| P02 — SQL interpolado | ok | 712.56 |  |
| P03 — SQL con formato | ok | 646.48 |  |
| P04 — Identificador SQL externo | ok | 616.97 |  |
| P07 — os.system externo | ok | 606.24 |  |
| P08 — subprocess shell | ok | 640.39 |  |
| P09 — os.popen externo | ok | 829.04 |  |
| P10 — Comando interpolado | ok | 713.49 |  |
| P13 — eval externo | ok | 865.15 |  |
| P14 — exec externo | ok | 664.82 |  |
| P15 — eval en función | ok | 672.26 |  |
| P16 — eval tras strip | ok | 750.22 |  |
| P21 — Contrase?a codificada | ok | 686.95 |  |
| P23 — Path Traversal con entrada externa | ok | 713.52 |  |
| P25 — Contrase?a de base de datos codificada | ok | 623.24 |  |
| P26 — Token de acceso codificado | ok | 610.87 |  |
| P27 — Credenciales en cadena de conexi?n | ok | 581.94 |  |
| P28 — Path Traversal mediante concatenaci?n | ok | 571.05 |  |
| P29 — Path Traversal mediante pathlib | ok | 563.9 |  |
| P30 — Extracci?n ZIP vulnerable a Zip Slip | ok | 590.92 |  |
| P05 — SQL parametrizado | ok | 582.34 |  |
| P06 — Tabla permitida | ok | 567.21 |  |
| P11 — Argumentos constantes | ok | 582.95 |  |
| P22 — Clave API ficticia | ok | 578.91 |  |
| P24 — Ruta validada dentro del directorio | ok | 592.79 |  |
