# Sustentación de doce minutos: agente v2 y presupuesto

Preparación vigente: 7 de noviembre de 2026, base integrada
`467d00e0d56a98cd758f382a5c713737eb490845` (PR #48). La comparación real final de
veinte casos sigue pendiente de las evidencias de Christian. No se afirma mejora
de precisión del agente.

- [Presentación editable preparada para el cierre](CODEGUARD-cierre-20261107.pptx).
- [PDF de esta preparación](CODEGUARD-cierre-20261107.pdf).
- [Guion y fuentes](guion-12-minutos.md).
- [Plantilla y criterios para incorporar la comparación final](comparacion-final-pendiente.md).
- [Trazabilidad frontend](../29-revision-frontend-agente-presupuesto.md).

Se conservan como históricos el [PPTX del 6 de noviembre](CODEGUARD-borrador-12-minutos.pptx)
y su [PDF](CODEGUARD-12-minutos.pdf). No contienen la política de prioridad ni las
comprobaciones nuevas de esta preparación. Usar la versión vigente al ensayar.

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
| 12 | Comparación final pendiente y condiciones comunes | 50 |
| **Total** | | **720** |

Doce minutos planificados, sin preguntas; no es un ensayo cronometrado. Ronald
indicó que el reparto depende de las instrucciones del ingeniero para el 7 de
noviembre. No se asignan expositores todavía. Se preparó una
[hoja de coordinación y medición](ensayo-cronometrado.md), pendiente de completar
con datos reales. Las notas contienen fuentes y límites de cada afirmación.

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
severidad × confianza está integrada en PR #48 y se explica sin atribuir a Gemini
la confianza de Bandit ni afirmar una mejora en la evaluación final.

## Publicación y paquete

La versión histórica proviene del PR #39 y de la revisión incorporada por PR #46.
Esta preparación se entrega en `docs/cierre-agente-presupuesto-ronald`, separada
del acceso del PR #50. El README identifica qué archivos corresponden a cada fecha.
Christian debe regenerar el ZIP desde el commit de entrega acordado que incluya
estos archivos y, posteriormente, los resultados finales. No alterar manualmente
el manifiesto del ZIP anterior. Esta preparación no activa flags ni despliega.

## Actualización pendiente tras PR #52

Este candidato incorpora v2 de hasta cuatro pasos, ventana ±6 y contadores del SDK. El PPTX/PDF del 7 de noviembre se preserva tal como lo entregó Ronald; deberá regenerarse con estos límites y los resultados reales finales. La prioridad de ordenación está integrada. El candidato posterior del PR #54 incorpora severidad derivada y herencia verificable; consultar docs/35 y docs/36. Incorporar esta distinción y sus límites al regenerar el PDF, que sigue siendo una preparación y no una versión final.
