# 18. Comparación de semanas y rutas

Actualización del 7 de noviembre de 2026. Se conservan las evidencias históricas;
la comparación real actual está en `evidencias/semana-4/comparacion-real-8e66b2c-20261107/`.
Los resultados no son una prueba de generalización a todos los repositorios.

## Recuperación documental histórica

| Medida | Semana 3 | Semana 4, recuperación local PR #37 |
|---|---:|---:|
| Casos | 20 (18 con referencias esperadas) | 20 (18 con referencias esperadas) |
| Reglas curadas | 4 | 6 |
| Precision@3 | 0,5370 | 0,4630 |
| Recall@3 | 0,9444 | 0,8056 |
| MRR@3 | 0,8889 | 0,8611 |
| Hit@3 | 0,9444 | 0,8889 |

La recuperación empeoró en estas medidas aunque aumentó el corpus. No esconder
esa diferencia ni atribuir causalidad al agente: son medidas de recuperación
local con corpus distinto, no precisión de hallazgos ni latencia de Railway.
Fuentes: [semana 3](evidencias/semana-3/rag-20-casos/resumen.md) y
[semana 4](evidencias/semana-4/postmerge-caecd71-20261106/recuperacion-local-20/resumen.md).

## Generación histórica de la ruta directa

La corrida del PR #37, revisión `caecd71`, completó 20/20 informes con Gemini
real en Railway: TP/FP/FN 12/0/0, precisión/recall/F1 1,0; referencias resueltas
14/14, media 5,96 s y p95 8,11 s. Es la ruta directa, no el agente v2 actual.
La evaluación local de Semana 3 recibió 20 errores 503 por falta de clave:
no tiene precisión de Gemini calculable. Nunca sustituir esos fallos por datos
posteriores. Fuente: [validación histórica](24-validacion-real-postmerge.md).

## Comparación actual de ambas rutas

La corrida nueva conserva los mismos veinte casos y etiquetas, alterna el orden
por par y solicita explícitamente agente v2 con máximo cuatro pasos. Usa la
revisión `8e66b2cc3f10b67589edd3714de17dcc8246d729`, verificada en Railway. No
reintenta desde el evaluador ni modifica etiquetas después de observar respuestas.

Consultar [tabla generada](evidencias/semana-4/comparacion-real-8e66b2c-20261107/comparacion.md),
[JSON](evidencias/semana-4/comparacion-real-8e66b2c-20261107/resultados.json) y
[protocolo](27-protocolo-comparacion-rutas.md). TP/FP/FN se comparan sobre los mismos
pares completos. Errores, parciales y abstenciones permanecen en los cuarenta
registros. Consumo medido procede del SDK y conserva null si es desconocido.

La configuración de modelo y límites se contrastó con la versión y variables
públicas del despliegue. No se pudo atestar la huella del índice persistente
activo: la corrida está identificada como exploratoria respecto a ese control.
No confundir estabilidad del esquema con atestación de código ni afirmar ahorro
o superioridad por tener más herramientas. La revisión de pertinencia de citas
se registra separadamente del emparejamiento automático de hallazgos.

## Planificador y alcance

El [A/B histórico](evidencias/semana-4/agente-ab-20261105T190848Z/resumen.md)
recorrió seis casos/doce decisiones; cinco pares completos, sin cambio de
herramienta. Corresponde al planificador anterior. El ejecutor actualizado
`eval/evaluar_planificador_agente.py` permite una nueva corrida v2 sin/con evidencia
estática, pero requiere una credencial en el entorno autorizado de ejecución.
No presentar los cuarenta informes HTTP como ese experimento causal distinto.

Las pruebas controladas de v2 y de severidad verifican contratos y regresiones,
no la precisión de Gemini. La [matriz actual de cierre](37-cierre-verificado.md)
separa estas comprobaciones de los resultados reales y de las actividades humanas.

## Histórico conservado

La comparación redactada el 5 de noviembre, con los estados entonces pendientes,
se conserva en [histórico](historico/18-comparacion-20261105.md). La mejora de
resiliencia, integración y trazabilidad no implica por sí sola mayor recall.
