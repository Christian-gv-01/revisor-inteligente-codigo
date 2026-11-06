# Sustentación de 12 minutos — resultados del PR #37

Actualizado con las evidencias del 6 de noviembre de 2026 para revisión del equipo.
Versión evaluada: `caecd719a92fa40c060f24051b765e77721ee19b`, integrada por
[PR #36](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/36).
Los resultados de Gemini real, Railway y trazabilidad proceden del
[PR #37](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37)
y del [informe de validación](../24-validacion-real-postmerge.md).

Archivo editable, conservando su nombre para mantener los enlaces existentes:
[CODEGUARD-borrador-12-minutos.pptx](CODEGUARD-borrador-12-minutos.pptx).
Versión para exponer: [CODEGUARD-12-minutos.pdf](CODEGUARD-12-minutos.pdf).
Las notas de cada diapositiva contienen explicación, tiempo y fuentes del repositorio.
También están disponibles como [guion de lectura](guion-12-minutos.md).

| Diapositiva | Contenido | Segundos |
|---|---|---:|
| 1 | Proyecto y equipo | 30 |
| 2 | Problema y valor esperado | 60 |
| 3 | Flujo y arquitectura | 60 |
| 4 | Procedencia de resultados | 70 |
| 5 | Confirmación humana | 70 |
| 6 | Demostración local | 70 |
| 7 | Prioridad y estado parcial | 60 |
| 8 | Resultados con Gemini real | 60 |
| 9 | Fuentes y cobertura | 60 |
| 10 | Integración, CI y despliegue | 60 |
| 11 | Documentación e historias | 70 |
| 12 | Resultados, límites y siguientes pasos | 50 |
| **Total** | | **720 (12 minutos)** |

El tiempo es un guion de ensayo, no una duración medida. Ajustar el reparto de
expositores con el equipo. Ronald asume Frontend y documentación en la asignación
actual; no se asigna a Andy un rol nuevo sin confirmación.

La demo usa el ejemplo SQL local. Mostrar la casilla inicialmente desmarcada,
cancelar, volver a previsualizar y confirmar una copia con otro nombre. No abrir ni
ejecutar el `.py`. Las capturas de respaldo están identificadas como simuladas.

La integración de frontend y backend está completada. La API de correcciones se
probó en Railway por HTTP con propuestas reales. La opción de correcciones en la
interfaz pública permanece deshabilitada por defecto según el PR #37: no confundir
esa decisión de activación con una integración aún por implementar.

## Alcance de los resultados presentados

- CI de integración: 296 backend/QA, 91 unitarias frontend y 24/24 HTTP con estático.
  Sin estático: 19 aprobadas y cinco no aplicables. Las específicas están incluidas.
- Interfaz: siete escenarios con FastAPI/SQLite reales y Gemini simulado,
  además de ocho casos demo. Caducidad 410 y flujo visual pertenecen a este entorno.
- Gemini real: 20/20 informes completos y coincidencias con referencia, TP 12 / FP 0 /
  FN 0 y 14/14 referencias resueltas. Media 5964,98 ms y p95 8107,56 ms.
- Railway sobre caecd71: 26/26 escenarios públicos y nueve aserciones HTTP del
  agente/correcciones. P26 solo evalúa AST local.
- Recuperación local: Recall@3 0,8056 y Precision@3 0,4630, con 18 casos que tienen
  referencias esperadas dentro del conjunto de veinte.

Es una sola corrida pequeña del flujo directo. No prueba generalización, calidad
semántica de cada parche ni una mejora causal del agente. La presentación y las
notas conservan esos límites. Esta actualización documental no vuelve a ejecutar
Gemini, no activa funciones en producción y no atribuye a Ronald las corridas de Christian.

El ZIP recibido corresponde a `ec516313e48664dddfae7b1a28ebe7a6850725ae` y conserva
el borrador anterior sin PDF. Para incorporar esta actualización, el responsable
del paquete debe regenerarlo desde el commit que incluya los archivos nuevos;
no modificar manualmente el manifiesto del ZIP original.
