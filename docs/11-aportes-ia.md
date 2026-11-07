# 11. Aportes del equipo y declaración de uso de IA

## Cierre documental — 7 de noviembre de 2026

Ronald confirmó el nombre completo de **Klever Andres Alban Cruz (Andy)**.
Los integrantes son Ronald Yépez, Klever Andres Alban Cruz y Christian Gamboa.
Esta confirmación no reasigna identidades Git ni sustituye aceptaciones académicas.

En el cierre, Ronald entrega **frontend y documentación del producto**: revisión
del consentimiento y presupuesto, trazabilidad, documento principal del agente,
verificación de requisitos/fuentes y preparación de presentación. Los PR #46,
#50 y #51 conservan sus cambios y pruebas. Los aportes iniciales de QA se mantienen
identificados abajo. La implementación de severidad derivada, YAML y herencia
corresponde al trabajo de Backend comunicado en PR #55; no se atribuye a Ronald.
Christian coordina la integración, la evaluación real, Railway y el paquete final.

La base técnica de cierre es `b6ce96c926631ea913f467be291228f705b8b5c6`.
Su CI tiene ocho verificaciones aprobadas. La evaluación real no demostró una
mejora de precisión del agente; se conserva esa conclusión y sus límites.
El cierre técnico no acredita por sí solo ensayo, instalación por otro integrante
ni registro de entrega. La correspondencia de cuentas históricas y cualquier
aceptación exigida por el docente debe conservar su evidencia real.

## Nueva asignación — 6 de noviembre de 2026

Ronald confirmó que en esta etapa asume **Compañero 2: Frontend y documentación
del producto**. Su aporte local comprende interfaz de aprobación/cancelación,
prioridad y estado parcial, ocho historias específicas, contrato propuesto con
Christian y borrador de presentación de doce minutos. Ver
[21-frontend-producto.md](21-frontend-producto.md).

En esa asignación, Christian conservaba la responsabilidad de los endpoints del backend. No se
reinterpreta como trabajo de Ronald la implementación de esos endpoints ni las
199 pruebas comunicadas por Christian. La tabla siguiente conserva los roles
informados el 5 de noviembre, anteriores al reparto de cierre.

## Responsabilidades históricas confirmadas el 5 de noviembre

Información proporcionada por Ronald el 5 de noviembre de 2026. La tabla distingue
responsabilidad de esa fecha y autoría histórica, y no sustituye la aprobación final de
cada integrante.

| Integrante | Rol confirmado | Entregables asociados |
|---|---|---|
| Ronald Yépez | QA, seguridad y documentación | Matriz pública, revisión de errores/entradas, auditoría, trazabilidad y consolidación documental |
| Klever Andres Alban Cruz (Andy) | Frontend y evaluación, en la asignación del 5 de noviembre | Interfaz, visualización y exportación, dataset, métricas, comparación final y presentación |
| Christian Gamboa | Backend, IA, agente y despliegue | API, proveedor, RAG/agente, analizadores estáticos, Docker, Railway y volumen |

El nombre completo de Andy se confirmó el 7 de noviembre. Ronald
confirmó para este trabajo la cuenta `0123445-20Alexis`. No se asignan otras cuentas
a personas por inferencia ni se cambia el autor registrado de commits previos.

## Participación identificada

La siguiente relación se basa en el historial Git y debe ser validada por el equipo antes de la entrega final.

| Identidad Git | Aportes observables |
|---|---|
| `christian` / `Christian-gv-01` | Backend FastAPI, Gemini, carga de archivos y ZIP, repositorios GitHub, agente supervisado y preparación de despliegue. |
| `Andyjr98` | QA, seguridad de entradas, RAG, filtros, abstención, regresiones y documentación de decisiones. |
| `olmesaguilar` | Frontend, diseño, trazabilidad de fuentes, evaluación RAG e integración HTTP, según el historial. |

Las identidades Git describen autoría registrada; no acreditan por sí solas el nombre ni el rol actual de la persona. La correspondencia de las cuentas históricas con integrantes debe confirmarla el equipo. El responsable de Frontend y Evaluación comunicó sus avances por separado. Ronald confirmó la cuenta `0123445-20Alexis` y su rol inicial de Compañero 3, QA, seguridad y documentación; desde el 6 de noviembre asume frontend y documentación. Esto no cambia la autoría histórica de los commits.

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
