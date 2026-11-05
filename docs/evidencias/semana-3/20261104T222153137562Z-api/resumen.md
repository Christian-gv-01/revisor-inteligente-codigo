# Evaluación api

Fecha UTC: 2026-11-04T22:21:53.246134+00:00

Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.

| Métrica | Valor |
|---|---:|
| total | 25 |
| completados | 25 |
| errores | 0 |
| tasa_completitud | 1.0 |
| latencia_media_ms | 4205.8504 |
| latencia_p95_ms | 6482.97 |
| precision_at_k | 0.44 |
| recall_at_k | 0.92 |
| mrr_at_k | 0.96 |
| hit_at_k | 0.96 |
| sin_fuentes_fuera_cobertura | No disponible |
| casos_con_referencias_esperadas_evaluados | 25 |
| tp | 20 |
| fp | 0 |
| fn | 0 |
| hallazgos | 20 |
| hallazgos_con_citas_resueltas | 20 |
| referencias | 22 |
| referencias_resueltas | 22 |
| lineas_fuera_rango | 0 |
| precision | 1.0 |
| recall | 1.0 |
| f1 | 1.0 |
| cobertura_citas | 1.0 |
| validez_referencias | 1.0 |
| tasa_abstencion | 0 |
| exactitud_casos_validos | 1 |
| aciertos_sobre_total | 1.0 |

## Casos

| Caso | Estado | Tiempo (ms) | Error |
|---|---|---:|---|
| P01 — SQL concatenado | ok | 13957.52 |  |
| P02 — SQL interpolado | ok | 3457.21 |  |
| P03 — SQL con formato | ok | 3651.5 |  |
| P04 — Identificador SQL externo | ok | 3459.42 |  |
| P07 — os.system externo | ok | 3376.81 |  |
| P08 — subprocess shell | ok | 6482.97 |  |
| P09 — os.popen externo | ok | 3226.77 |  |
| P10 — Comando interpolado | ok | 3129.0 |  |
| P13 — eval externo | ok | 3040.99 |  |
| P14 — exec externo | ok | 3741.01 |  |
| P15 — eval en función | ok | 3551.85 |  |
| P16 — eval tras strip | ok | 3260.83 |  |
| P21 — Contrase?a codificada | ok | 4061.39 |  |
| P23 — Path Traversal con entrada externa | ok | 5564.27 |  |
| P25 — Contrase?a de base de datos codificada | ok | 3388.27 |  |
| P26 — Token de acceso codificado | ok | 3389.38 |  |
| P27 — Credenciales en cadena de conexi?n | ok | 4047.37 |  |
| P28 — Path Traversal mediante concatenaci?n | ok | 3476.15 |  |
| P29 — Path Traversal mediante pathlib | ok | 3585.8 |  |
| P30 — Extracci?n ZIP vulnerable a Zip Slip | ok | 5852.93 |  |
| P05 — SQL parametrizado | ok | 4195.77 |  |
| P06 — Tabla permitida | ok | 3360.94 |  |
| P11 — Argumentos constantes | ok | 2929.58 |  |
| P22 — Clave API ficticia | ok | 2776.25 |  |
| P24 — Ruta validada dentro del directorio | ok | 4182.28 |  |
