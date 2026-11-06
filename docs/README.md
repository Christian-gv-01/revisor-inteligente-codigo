# Documentación de CODEGUARD

Nueva asignación del 6 de noviembre: [Frontend y documentación del producto](21-frontend-producto.md),
[contrato propuesto de confirmación](20-contrato-confirmacion-humana.md) y
[borrador de presentación de doce minutos](presentacion/README.md).

Consolidación del 5 de noviembre de 2026 sobre `main` en `65675e2`.
Responsable de esta edición: Ronald Yépez, QA, seguridad y documentación.

## Lectura principal

| Documento | Propósito |
|---|---|
| [01. Propuesta](01-propuesta.md) | Problema, usuarios, alcance, modelo y riesgos |
| [02. Requisitos](02-requisitos.md) | Doce historias Dado/Cuando/Entonces, RF/RS y umbrales medibles |
| [03. Arquitectura](03-arquitectura.md) | C4, secuencia y modalidades vigentes |
| [04. Fuentes](04-fuentes.md) | Inventario, revisión y fragmentación |
| [Levantamiento](levantamiento.md) | Dieciocho preguntas y estado de respuestas reales |
| [05. Prompts](05-prompts.md) | Experimentos históricos y distinción del prompt activo |
| [06. RAG](06-rag.md) | Ingesta, metadatos, recuperación y abstención |
| [07. Evaluación](07-evaluacion.md) | Resultados originales de Semana 3 |
| [08. Pruebas](08-pruebas.md) | Matriz, errores, entradas, regresiones y evidencia |
| [09. Decisiones](09-decisiones.md) | Decisiones vigentes, alternativas y consecuencias |
| [10. Análisis estático](10-analisis-estatico.md) | Ruff/Bandit, límites, contrato y estados |
| [11. Aportes e IA](11-aportes-ia.md) | Responsables confirmados, autoría y herramientas |
| [12. Cierre QA](12-cierre-qa-entrega4.md) | Integración, producción, reinicio y riesgos pendientes |
| [17. Agente integrado](17-agente-integrado.md) | Evidencia tipada, síntesis y trazas en React |
| [18. Comparación](18-comparacion-semanas-3-4.md) | Diferencias de configuración y resultados comparables |
| [19. Cierre documental](19-cierre-documental.md) | Cumplimiento documental y pendientes reales por responsable |
| [Datos e IA](tratamiento-datos.md) | Qué se procesa, destinatarios y limitaciones |
| [Despliegue](despliegue.md) | Docker, variables, Railway y persistencia |
| [Guion QA](guion-qa.md) | Explicación del aporte de Ronald y preguntas de sustentación |

## Evidencia y revisiones especializadas

- [Semana 1: registro de originales faltantes](evidencias/semana-1/README.md).
- [Semana 4: evidencias versionadas](evidencias/semana-4/README.md).
- [Revisión PR #19](14-revision-qa-pr19.md) y
  [verificación pública propia](15-verificacion-publica-integrada.md).
- [Auditoría histórica de integración](16-auditoria-entrega-integracion.md).
- [Agente inicial](08-agente.md), [evaluación del planificador](10-evaluacion-planificador.md)
  y [resiliencia de Gemini](11-resiliencia-gemini.md).
- [Integración frontend/evaluador](integracion-frontend-evaluacion.md) y
  [revisión de seguridad](revision-seguridad.md).
- [Arquitectura y ADR históricos](historico/README.md).

Se conservan nombres numerados heredados para no romper referencias. El número
de archivo no representa la fecha de la última ejecución. Una prueba local, una
respuesta simulada y una ejecución pública son evidencias distintas.
