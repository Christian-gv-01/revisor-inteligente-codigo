# Preparación de la comparación final

Preparación de Ronald, 7 de noviembre de 2026. **No contiene resultados finales.**
Christian coordina la evaluación real. La presentación mantiene doce diapositivas
y 720 segundos planificados, sin acreditar ensayo ni reparto de expositores.

## Datos que deben acompañar los resultados

| Dato | Registro por completar con evidencia |
|---|---|
| Commit probado, fecha y entorno | Pendiente |
| Dataset de veinte casos y SHA-256 | Pendiente |
| Corpus/índice y versiones del evaluador | Pendiente |
| Modelo, configuración y límites | Pendiente |
| Ruta directa y agente v2 bajo las mismas condiciones | Pendiente |
| Reintentos, errores, parciales y abstenciones por caso | Pendiente |
| Artefacto original de cada corrida | Pendiente |
| Revisión de pertinencia de citas y criterio de emparejamiento | Pendiente |

No rellenar ausencias con cero ni excluir errores para mejorar cifras. Si las
condiciones difieren, describirlas y limitar la comparación. Los veinte casos
no representan todos los repositorios ni prueban mejora causal general.

## Tabla preparada para el informe

| Medida | Flujo directo | Agente v2 | Denominador / definición |
|---|---|---|---|
| Casos completados, parciales y fallidos | Pendiente | Pendiente | Mismos 20 casos |
| TP, FP y FN | Pendiente | Pendiente | Emparejamiento declarado del evaluador |
| Precisión | Pendiente | Pendiente | TP / (TP + FP); indicar indefinida si no hay denominador |
| Recall | Pendiente | Pendiente | TP / (TP + FN); indicar indefinida si no hay denominador |
| F1 | Pendiente | Pendiente | Según precisión/recall definidos; no convertir ausencias en cero |
| Latencia media y P95 | Pendiente | Pendiente | Unidad, muestra y tratamiento de errores declarados |
| Intentos reales al proveedor | Pendiente | Pendiente | Incluir reintentos, sin equipararlos a pasos |
| Citas resolubles y pertinencia revisada | Pendiente | Pendiente | Separar existencia de ID de corrección semántica |

Recall@K, Precision@K y MRR del recuperador son métricas diferentes de precisión
y recall de hallazgos. Se conservan por separado con sus conjuntos y versiones.

## Sustitución en las doce diapositivas

- Diapositiva 8: conserva la corrida histórica del PR #37 en `caecd71`. Si se
  sustituye por la comparación final, guardar esa referencia histórica en notas
  y documentos, y citar el nuevo artefacto y commit en pantalla.
- Diapositiva 9: mantener resultados de recuperación etiquetados como históricos
  salvo que se entregue otra evaluación documental comparable.
- Diapositiva 10: conservar el alcance simulado de las pruebas de software. No
  reemplazar su conteo por casos de evaluación ni sumarlos como una misma suite.
- Diapositiva 12: sustituir «Comparación final pendiente» por la conclusión que
  permitan los datos, incluyendo empates, empeoramientos o incertidumbre.
- Actualizar las notas y el guion de esas diapositivas; volver a comprobar el
  tiempo real con el equipo. El resto no requiere rehacerse.

Frase válida mientras no llegan resultados: «El agente integra herramientas y
fuentes verificables. La comparación real con el flujo directo sigue pendiente;
todavía no afirmamos una mejora de precisión».

No cambiar flags, corpus, dataset ni producción para preparar la presentación.
