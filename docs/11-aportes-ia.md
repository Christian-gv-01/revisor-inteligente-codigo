# 11. Aportes del equipo y declaración de uso de IA

## Integrantes y responsabilidades confirmadas

Información proporcionada por Ronald el 5 de noviembre de 2026. La tabla distingue
responsabilidad actual de autoría histórica y no sustituye la aprobación final de
cada integrante.

| Integrante | Rol confirmado | Entregables asociados |
|---|---|---|
| Ronald Yépez | QA, seguridad y documentación | Matriz pública, revisión de errores/entradas, auditoría, trazabilidad y consolidación documental |
| Andy | Frontend y evaluación | Interfaz, visualización y exportación, dataset, métricas, comparación final y presentación |
| Christian Gamboa | Backend, IA, agente y despliegue | API, proveedor, RAG/agente, analizadores estáticos, Docker, Railway y volumen |

Se conserva «Andy» tal como fue confirmado; su apellido no fue aportado. Ronald
confirmó para este trabajo la cuenta `0123445-20Alexis`. No se asignan otras cuentas
a personas por inferencia ni se cambia el autor registrado de commits previos.

## Participación identificada

La siguiente relación se basa en el historial Git y debe ser validada por el equipo antes de la entrega final.

| Identidad Git | Aportes observables |
|---|---|
| `christian` / `Christian-gv-01` | Backend FastAPI, Gemini, carga de archivos y ZIP, repositorios GitHub, agente supervisado y preparación de despliegue. |
| `Andyjr98` | QA, seguridad de entradas, RAG, filtros, abstención, regresiones y documentación de decisiones. |
| `olmesaguilar` | Frontend, diseño, trazabilidad de fuentes, evaluación RAG e integración HTTP, según el historial. |

Las identidades Git describen autoría registrada; no acreditan por sí solas el nombre ni el rol actual de la persona. La correspondencia de las cuentas históricas con integrantes debe confirmarla el equipo. El responsable de Frontend y Evaluación comunicó sus avances por separado. El usuario de esta entrega confirmó la cuenta `0123445-20Alexis` y asume el rol de Compañero 3, QA, seguridad y documentación; esta confirmación no cambia la autoría histórica de los commits.

## Aporte del rol QA, seguridad y documentación — Entrega 4

- Consolidación de propuesta y requisitos.
- Matriz de 26 escenarios HTTP reproducibles.
- Regresiones de prompt injection y sanitización de errores 422.
- Auditoría automatizada de secretos e historial.
- Procedimiento automatizado para comparar citas antes y después del reinicio.
- README reproducible y organización de evidencias de semana 4.
- Aceptación del contrato Ruff/Bandit en las cuatro modalidades y comprobación con analizadores reales.
- Primera ejecución pública 24/26; ejecución posterior propia 26/26, preservadas por separado. Ver [verificación pública](15-verificacion-publica-integrada.md).
- Comprobación del HTTP 429 con evidencia sin cuerpos sensibles.
- Revisión del panel/exportación estática y regresiones de la integración del PR #19.
- Consolidación del inventario, doce historias de usuario, arquitectura vigente, decisiones y comparación documental de semanas.
- Registro de límites y pendientes reales en [cierre documental](19-cierre-documental.md). El reinicio y su log fueron aportados posteriormente por Christian; no se atribuyen a Ronald.

## Herramientas de inteligencia artificial

### Google Gemini

Es un componente funcional del producto. Recibe código y contexto documental como datos no confiables y genera un informe estructurado. Su salida se valida con Pydantic, límites de líneas y referencias RAG. Las pruebas automatizadas normalmente utilizan mocks para no consumir cuota ni confundir una respuesta controlada con una evaluación real.

### OpenAI Codex

Se utilizó como apoyo en la Entrega 4 para analizar el repositorio, proponer pruebas, crear scripts reproducibles, organizar documentación y revisar coherencia técnica. Las acciones fueron supervisadas en el repositorio; los comandos de prueba y sus resultados se conservan como evidencia. Codex no sustituye la revisión, aceptación ni autoría responsable del equipo.

## Principios aplicados

- No presentar texto generado por IA como evidencia ejecutada.
- No incluir claves, datos personales o código confidencial en prompts o capturas.
- Revisar manualmente cambios y resultados antes del Pull Request.
- Identificar claramente mocks, modo demo y respuestas reales.
- Mantener trazabilidad mediante ramas, commits, pruebas y archivos de evidencia.

## Declaración final

El equipo conserva la responsabilidad sobre la arquitectura, el código, la seguridad, las pruebas y las conclusiones. El uso registrado de IA incluye el componente Gemini y la asistencia de Codex en este trabajo. La evidencia permite comprobar los cambios y pruebas indicados, pero no implica que todos los integrantes hayan aprobado cada sugerencia. Cualquier otra herramienta utilizada individualmente y la revisión final de aportes deben añadirse antes de la entrega. No se certifica una aceptación grupal que no haya sido comunicada.
