El cierre vigente tras la revisión del 7 de noviembre se registra en
[evidencias de revisión 7](evidencias/semana-4/revision7-cierre-20261107/README.md):
Directa inicial / Agente opcional y presentación única de diez diapositivas.

# Documentación de CODEGUARD

[Cierre de la entrega documental de Ronald](entrega-ronald-20261107.md): nombres
confirmados, paquete verificado de `b6ce96c` y alcance de las actividades humanas.

Estado vigente: [37. Cierre verificado](37-cierre-verificado.md), con trazabilidad
frente a la revisión docente de `605d142`, funcionalidades integradas y límites.

- [Agente supervisado: documento principal](08-agente.md). El documento 17 remite aquí.
- [Comparación real de rutas y semanas](18-comparacion-semanas-3-4.md), incluyendo resultados desfavorables.
- [Severidad derivada e herencia verificable](35-severidad-derivada-herencia.md).
- [Corrección integrada PR #55](36-correccion-herencia-integrada.md).
- [Presentación y PDF](presentacion/README.md), con tiempo planificado y fuentes.
- [Instalación desde checkout limpio](30-instalacion-checkout-limpio.md) y [ensayo humano pendiente](presentacion/ensayo-cronometrado.md).

Los registros por PR conservan sus revisiones originales; un resultado antiguo
no certifica la versión pública actual. No sumar pruebas de suites incluidas
ni presentar mocks como precisión de Gemini.

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
| [08. Agente](08-agente.md) | Documento principal: herramientas, límites, evidencia y evaluación |
| [17. Referencia histórica](17-agente-integrado.md) | Remite al documento principal 08 |
| [18. Comparación](18-comparacion-semanas-3-4.md) | Diferencias de configuración y resultados comparables |
| [19. Cierre documental](19-cierre-documental.md) | Cumplimiento documental y pendientes reales por responsable |
| [Datos e IA](tratamiento-datos.md) | Qué se procesa, destinatarios y limitaciones |
| [Despliegue](despliegue.md) | Docker, variables, Railway y persistencia |
| [Guion QA](guion-qa.md) | Explicación del aporte de Ronald y preguntas de sustentación |

## Entrega para la prueba conjunta

- [Rama frontend, comandos, variables y casos de integración](22-entrega-frontend-integracion.md).

## Evidencia y revisiones especializadas

- [Abstención explícita y conservación parcial](26-abstencion-parcial.md).
- [Reintentos del proveedor y presupuesto compartido](reintentos-presupuesto.md).
- [Contrato optativo v2 del agente y ejemplos JSON](contrato-agente-v2/README.md).
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
