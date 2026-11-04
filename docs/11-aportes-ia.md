# 11. Aportes del equipo y declaración de uso de IA

## Participación identificada

La siguiente relación se basa en el historial Git y debe ser validada por el equipo antes de la entrega final.

| Identidad Git | Aportes observables |
|---|---|
| `christian` / `Christian-gv-01` | Backend FastAPI, Gemini, carga de archivos y ZIP, repositorios GitHub, agente supervisado y preparación de despliegue. |
| `Andyjr98` | QA, seguridad de entradas, RAG, filtros, abstención, regresiones y documentación de decisiones. |
| `olmesaguilar` | Frontend, diseño, trazabilidad de fuentes, evaluación RAG e integración HTTP, según el historial. |

Las identidades Git describen autoría registrada; no acreditan por sí solas el nombre ni el rol actual de la persona. La correspondencia entre cuentas e integrantes debe confirmarla el equipo. El responsable de Frontend y Evaluación comunicó sus avances por separado; el usuario de esta entrega asume el rol de Compañero 3, QA, seguridad y documentación. No se atribuye este rol a la cuenta configurada localmente sin esa confirmación.

## Aporte del rol QA, seguridad y documentación — Entrega 4

- Consolidación de propuesta y requisitos.
- Matriz de 26 escenarios HTTP reproducibles.
- Regresiones de prompt injection y sanitización de errores 422.
- Auditoría automatizada de secretos e historial.
- Procedimiento automatizado para comparar citas antes y después del reinicio.
- README reproducible y organización de evidencias de semana 4.
- Registro explícito de pendientes que requieren URL pública, sin inventar resultados.

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

El equipo conserva la responsabilidad sobre la arquitectura, el código, la seguridad, las pruebas y las conclusiones. Las herramientas de IA se utilizaron como asistencia técnica; sus sugerencias fueron verificadas mediante código, documentación oficial y pruebas reproducibles. Cualquier otra herramienta de IA utilizada individualmente debe añadirse a este documento antes de la entrega.
