# Sustentación: cierre técnico y comparación real

Preparación actualizada el 7 de noviembre de 2026. Doce diapositivas, 720 segundos
planificados. La comparación real corresponde a Railway `8e66b2c` y conserva el
resultado desfavorable del agente; no se afirma mejora de precisión.

- [Presentación editable actualizada](CODEGUARD-cierre-verificado-20261107.pptx).
- [PDF actualizado](CODEGUARD-cierre-verificado-20261107.pdf).
- [Guion con fuentes](guion-12-minutos.md).
- [Tabla de comparación real](../evidencias/semana-4/comparacion-real-8e66b2c-20261107/comparacion.md).
- [Cierre y pendientes verificables](../37-cierre-verificado.md).
- [Hoja de ensayo humano](ensayo-cronometrado.md).

Se conservan los PPTX/PDF anteriores con sus nombres y revisión. Usar el archivo
actualizado y revisar las notas antes del ensayo. La política de severidad puede
elevar el resultado, conservando siempre los valores originales y las reglas.

| Diapositiva | Contenido | Segundos |
|---|---|---:|
| 1 | Proyecto y versión | 30 |
| 2 | Problema y valor esperado | 60 |
| 3 | Arquitectura y modalidades | 60 |
| 4 | Agente v2 y límites | 70 |
| 5 | Copia corregida y aprobación | 70 |
| 6 | Presupuesto antes de analizar | 70 |
| 7 | Severidad verificable | 60 |
| 8 | Comparación real directa/agente | 60 |
| 9 | Fuentes y recuperación histórica | 60 |
| 10 | Pruebas de software | 60 |
| 11 | Trazabilidad documental | 70 |
| 12 | Conclusión y límites | 50 |
| **Total planificado** | | **720** |

Las cifras de IA y las pruebas simuladas tienen denominadores distintos. El
agente completó 20/20, pero tuvo F1 0,762 frente a 0,957 de la ruta directa,
mayor latencia y consumo. Diez finalizaciones tempranas no acreditan ahorro
causal. Las referencias resuelven, pero P06 muestra que pueden acompañar un
falso positivo. El índice activo no tuvo huella verificada.

El candidato corrige una pérdida de fuentes y activa confirmaciones en Docker;
no atribuirle cifras de la revisión anterior. Validar su despliegue y, si se
incorpora el cambio funcional, medir de nuevo sin borrar la corrida previa.

La exportación técnica y el tiempo planificado no sustituyen el ensayo del
 equipo, la instalación independiente ni la aprobación académica. La revisión
anterior de Ronald se conserva en el histórico. El ZIP se genera desde el Git
exacto que incorpora esta presentación y sus resultados.
