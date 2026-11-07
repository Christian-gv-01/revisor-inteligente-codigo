# 18. Comparación de semanas y rutas

Actualización del 7 de noviembre de 2026. Se conservan las evidencias históricas;
las dos corridas reales están en `evidencias/semana-4/comparacion-real-8e66b2c-20261107/` y
`evidencias/semana-4/postmerge-c522c24-20261107/`.
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

## Comparación anterior a la corrección de cobertura

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

## Comparación posterior sobre c522c24

Se ejecutaron los mismos veinte casos por ambas rutas en Railway, sin cambiar
etiquetas ni reintentar desde el evaluador. La directa completó 17/20 informes y
el agente 14/20. Hubo trece pares completos comunes, con TP/FP/FN 8/0/0 y F1 1,0
por ruta en ese subconjunto. Los tres y seis parciales permanecen en el JSON.
No comparar ese F1 selectivo con el de los veinte pares históricos para afirmar
una mejora. Los aciertos con informe completo sobre el total son 17/20 y 14/20.

La media global fue 10,34/22,62 s y el p95 21,07/43,45 s. Los intentos SDK fueron
21/71. Los tokens totales permanecen desconocidos por intentos sin respuesta:
las sumas conocidas 25.255 y 65.057 cubren 17/20 y 12/20 peticiones respectivamente.
El agente finalizó anticipadamente en 8/20 solicitudes. No demostró superioridad.

Se verificaron seis reglas activas coincidentes con el fuente y la misma huella
durante y después de la corrida. Falta la observación anterior a la primera
solicitud: la configuración inicial conserva null y su hash, sin cambiar el
carácter exploratorio del estudio. Hay revisión asistida de los 18 hallazgos,
no una revisión humana independiente ni ejecución de parches.

Consultar [evidencias y límites](evidencias/semana-4/postmerge-c522c24-20261107/README.md),
[tabla generada](evidencias/semana-4/postmerge-c522c24-20261107/comparacion-rutas/comparacion.md)
y [JSON original](evidencias/semana-4/postmerge-c522c24-20261107/comparacion-rutas/resultados.json).

## Planificador y alcance

El [A/B histórico](evidencias/semana-4/agente-ab-20261105T190848Z/resumen.md)
recorrió seis casos/doce decisiones; cinco pares completos, sin cambio de
herramienta. Corresponde al planificador anterior. La nueva corrida v2 se ejecutó dentro del contenedor autorizado sobre c522c24,
sin extraer su clave: doce decisiones, cinco pares completos, un par incompleto
por 503 y dos cambios entre los cinco pares comparables (40%). Se evalúa solo
la primera decisión, con Ruff/Bandit en ambos grupos, AB/BA y una repetición.
[Resultados A/B](evidencias/semana-4/postmerge-c522c24-20261107/planificador-ab/resumen.md).
El cambio de herramienta prueba influencia del contexto, no mejor precisión.
No presentar los cuarenta informes HTTP como ese experimento causal distinto.

Las pruebas controladas de v2 y de severidad verifican contratos y regresiones,
no la precisión de Gemini. La [matriz actual de cierre](37-cierre-verificado.md)
separa estas comprobaciones de los resultados reales y de las actividades humanas.

## Histórico conservado

La comparación redactada el 5 de noviembre, con los estados entonces pendientes,
se conserva en [histórico](historico/18-comparacion-20261105.md). La mejora de
resiliencia, integración y trazabilidad no implica por sí sola mayor recall.
