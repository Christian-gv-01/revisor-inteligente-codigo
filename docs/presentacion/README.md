# Sustentación de doce minutos: agente v2 y presupuesto

Referencia común: `9c97ca1c8797bad5bdfdf227dba119b7839d32c7` (PR #45).
Actualización de Ronald, 6 de noviembre de 2026. La comparación real final de
veinte casos aún debe incorporarse con las evidencias de Christian.

- [Presentación editable](CODEGUARD-borrador-12-minutos.pptx), con el nombre existente.
- [PDF para exposición](CODEGUARD-12-minutos.pdf).
- [Guion y fuentes](guion-12-minutos.md).
- [Trazabilidad frontend](../29-revision-frontend-agente-presupuesto.md).

| Diapositiva | Contenido | Segundos |
|---|---|---:|
| 1 | Proyecto y referencia común | 30 |
| 2 | Problema y valor esperado | 60 |
| 3 | Arquitectura y modalidades | 60 |
| 4 | Recorrido del agente v2 | 70 |
| 5 | Confirmación de copia corregida | 70 |
| 6 | Presupuesto ZIP/GitHub | 70 |
| 7 | Prioridad actual y estado parcial | 60 |
| 8 | Evaluación real histórica del PR #37 | 60 |
| 9 | Fuentes y recuperación histórica | 60 |
| 10 | Revisión frontend y pruebas controladas | 60 |
| 11 | Trazabilidad y documentación | 70 |
| 12 | Responsabilidades y evaluación final pendiente | 50 |
| **Total** | | **720** |

Doce minutos planificados, sin preguntas; no es un ensayo cronometrado. Acordar
el reparto de voces. Las notas contienen fuentes y límites de cada afirmación.

## Separación de resultados

La revisión propia registra 132 unitarias frontend, lint/build correctos, seis
escenarios de navegador v2 y nueve del presupuesto. Las 24 HTTP se omiten en la
suite unitaria sin servidor; no se presentan como repetidas aquí. Los runners
usan FastAPI/SQLite/RAG y herramientas reales con Gemini/GitHub simulados.

La diapositiva histórica conserva los veinte casos reales de caecd71 documentados
en PR #37: no son resultados de v2 ni comparación final. La recuperación local
tiene su propio denominador y entorno. No se afirma mejora de calidad,
generalización ni despliegue de la revisión nueva.

El presupuesto sigue apagado por defecto. Aprobar presupuesto autoriza analizar
una instantánea; aprobar una corrección autoriza descargar una copia. La política
severidad × confianza corresponde a Backend y no se declara terminada.

## Publicación y paquete

Esta edición continúa el PR #39, recuperado en la rama actual antes de actualizar
el contenido. Revisar los PR conjuntamente para evitar duplicar versiones.
Christian debe regenerar el ZIP desde el commit de entrega acordado que incluya
estos archivos y, posteriormente, los resultados finales. No alterar manualmente
el manifiesto del ZIP anterior. Esta preparación no activa flags ni despliega.
