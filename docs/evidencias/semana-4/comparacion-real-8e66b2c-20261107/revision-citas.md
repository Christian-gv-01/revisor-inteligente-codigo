# Revisión asistida de citas y errores

Fecha: 7 de noviembre de 2026. Revisión técnica por Codex de las respuestas, código del dataset y texto curado versionado. No es revisión independiente de un experto humano ni ejecución de las correcciones.

| Caso | Ruta | Ubicación | Referencias | Dictamen de pertinencia |
|---|---|---:|---|---|
| P01 | directa | 2 | seguridad_python-002, seguridad_python-004 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P01 | agente | 2 | seguridad_python-002 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P02 | agente | 2 | seguridad_python-002 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P02 | directa | 2 | seguridad_python-002, seguridad_python-004 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P03 | directa | 2 | seguridad_python-002, seguridad_python-004 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P03 | agente | 2 | seguridad_python-002 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P04 | agente | 2 | seguridad_python-002 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P04 | directa | 2 | seguridad_python-002, seguridad_python-004 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P06 | agente | 4 | seguridad_python-002 | Falso positivo: la referencia acepta opciones fijas y el código ya usa diccionario permitido. Un cambio futuro hipotético no prueba riesgo presente. |
| P07 | directa | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P07 | agente | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P08 | agente | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P08 | directa | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P09 | directa | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P09 | agente | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P10 | agente | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P10 | directa | 3 | seguridad_python-003 | Respalda el patrón observado; corrección requiere adaptación al controlador y contexto. |
| P13 | directa | 2 | seguridad_python-001 | Respalda evitar eval externo. literal_eval no es una solución universal ni limita por sí solo recursos. |
| P15 | directa | 2 | seguridad_python-001 | Respalda evitar eval externo. literal_eval no es una solución universal ni limita por sí solo recursos. |
| P16 | directa | 2 | seguridad_python-001 | Respalda evitar eval externo. literal_eval no es una solución universal ni limita por sí solo recursos. |

## Omisiones y causa investigada

- P14 (exec): omitido en ambas rutas; la directa se abstuvo. No convertir abstención en acierto ante una etiqueta positiva.
- P13/P15/P16: la ruta directa encontró eval y el agente no. Sus búsquedas por categoría devolvieron referencias 005/003 y sustituyeron la recuperación base. Es una pérdida de cobertura reproducible en el código; no demuestra que sea la única causa generativa.
- El candidato corrige la sustitución: conserva primero hasta tres fuentes base y completa con referencias elegidas por el planificador, máximo seis, sin modificar dataset ni etiquetas. Se añaden regresiones independientes del modelo.
- Se conserva esta corrida anterior al cambio. No atribuir los resultados a la corrección ni afirmar una mejora sin nueva ejecución sobre el candidato desplegado.

## Límites de la revisión

Las 24 referencias citadas resuelven por ID. Esa propiedad estructural no asegura pertinencia: P06 es el contraejemplo observado. Hay 20 hallazgos: 19 compatibles con las etiquetas y uno falso positivo. Las explicaciones generales no certifican explotabilidad, parches ejecutables, ausencia de otras vulnerabilidades ni cobertura de proyectos completos.
