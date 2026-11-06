# 18. Comparación documentada entre Semanas 3 y 4

Consolidación documental de Ronald Yépez, 5 de noviembre de 2026. Evaluación del
producto a cargo de Andy. Este documento compara evidencia existente; no registra
una nueva ejecución ni completa por sí solo la comparación generativa final.

## Configuración y resultados disponibles

| Dimensión | Semana 3 | Semana 4 | Interpretación permitida |
|---|---|---|---|
| Base | `8f27ddc` y cambios documentados en la corrida | Integraciones sucesivas hasta PR #31, `65675e2` | Son revisiones distintas; conservar hashes de cada evidencia |
| Dataset de recuperación | 20 casos, 18 con etiquetas y dos fuera de cobertura | No se localizó una corrida final equivalente que sustituya esa baseline | No calcular una mejora porcentual sin repetición comparable |
| Corpus y recuperación | Cuatro reglas; ChromaDB 1.5.9, distancia máxima 0,75, top 3 | Seis reglas; agente con hasta seis fuentes y flujo directo con límite tres | Cambiaron cobertura y presupuesto; no comparar automáticamente @3 con @6 |
| Recuperación | Completitud 20/20; Precision@3 0,5370; Recall@3 0,9444; MRR@3 0,8889; Hit@3 0,9444 | Sin métricas finales equivalentes registradas en este cierre | Son métricas de recuperación, no de hallazgos Gemini |
| Latencia de recuperación | Media 320,20 ms, p95 339,21 ms, tras calentamiento | Sin medición equivalente final | No compara latencia del agente completo |
| API del dataset | 20 respuestas 503 por proveedor local sin configurar | Casos reales locales/públicos con éxito y degradación; conjuntos distintos | Hay funcionamiento demostrado, no una métrica final de precisión |
| Integración HTTP | 9/9, proveedor simulado | 17/17 con estático y 12/12 aplicables con cinco omisiones en configuración alternativa | Verifica contratos; agente ejecuta estático en ambas configuraciones |
| Pruebas del producto | 58 frontend en la integración posterior; conteos iniciales preservados en informe de Semana 3 | Evidencia PR #31: 250 backend/QA y 76 frontend | El aumento de pruebas no es una medida de precisión de IA |
| Producción | No es el objetivo de la corrida local de recuperación | 26/26 escenarios públicos y continuidad de tres citas entre dos consultas | Falta log independiente del reinicio; no verifica toda la última integración |

Fuentes: [informe de Semana 3](07-evaluacion.md),
[recuperación de 20 casos](evidencias/semana-3/rag-20-casos/resumen.md),
[integración de Semana 3](evidencias/semana-3/integracion-http/README.md),
[validación PR #31](evidencias/semana-4/agente-integrado-20261105/validacion.json),
[contrato integrado](17-agente-integrado.md) y
[cierre público y reinicio](12-cierre-qa-entrega4.md).

Las cifras comunicadas por chat para otras corridas no reemplazan estos archivos.
Si el equipo aporta otro resultado, debe incorporarse con dataset, configuración
y fecha antes de compararlo.

## Otras evaluaciones de Semana 4

El [A/B del planificador](evidencias/semana-4/agente-ab-20261105T190848Z/resumen.md)
registra seis casos sintéticos, doce solicitudes y cinco pares completos; no hubo
cambios de herramienta en esos cinco pares. Evalúa una decisión, no la calidad
del informe final ni el recall de vulnerabilidades.

La [muestra de comparación](evidencias/semana-4/comparacion-muestra-20261105/resultados.json)
motivó integrar evidencia estática/AST en la síntesis. Sus conteos estáticos y
contextuales corresponden a capas distintas, no a riesgos independientes que
deban sumarse. Las regresiones controladas del PR #31 comprueban el cambio de
contrato y ubicación, sin demostrar una mejora general de Gemini.

## Protocolo pendiente para una comparación final válida

1. Congelar dataset y etiquetas antes de ejecutar. Registrar SHA del dataset,
   corpus, código, prompts, modelo, parámetros y modalidad de análisis.
2. Repetir un conjunto común con condiciones comparables. Si el endpoint cambia
   de directo a agente, separar la comparación del sistema de la recuperación.
3. Registrar TP, FP, FN, precisión, recall, F1, abstenciones, completitud, errores,
   latencia y tokens disponibles; no tratar errores como aciertos.
4. Revisar pertinencia de citas y correcciones. La existencia de IDs no demuestra
   su validez semántica. No atribuir tokens de una síntesis a todas las llamadas.
5. Guardar respuestas permitidas y resumen sin secretos. Indicar variabilidad,
   número de repeticiones y limitaciones; no escoger solo respuestas favorables.

El [evaluador existente](../eval/README.md) soporta el flujo directo. No afirmar que
evalúa el nuevo agente sin adaptar/verificar su ruta y contrato. No se ejecutaron
nuevas llamadas de pago para redactar esta comparación.

**Conclusión:** están documentados los cambios de cobertura, integración y
resiliencia. Sigue pendiente una medición equivalente de calidad generativa de
la versión final frente a Semana 3.
