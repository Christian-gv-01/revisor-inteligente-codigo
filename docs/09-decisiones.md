# 09. Decisiones técnicas y éticas

Actualización técnica: 7 de noviembre de 2026. Base integrada `8e66b2c` (PR #55).
El contrato de confirmación está implementado y probado en backend y frontend.
Su visibilidad pública depende del build; el candidato de cierre activa ambas
interfaces en Docker. La comprobación de despliegue debe registrar su SHA.
El historial conserva las decisiones originales y sus fechas.

Este registro describe decisiones implementadas y su justificación; no es un acta
de aprobación grupal. Se conserva el [registro de revisión 2](historico/09-decisiones-revision2.md).
Los identificadores E4 no reemplazan sus ADR históricos.

| ID | Decisión implementada | Alternativa y motivo | Consecuencia / verificación |
|---|---|---|---|
| E4-01 | Gemini encapsulado y modelo configurable | Cambiar de proveedor exige adaptador y nueva evaluación; solo estático no aporta síntesis RAG | Depende de cuota y disponibilidad; sin fallback Groq. [Propuesta](01-propuesta.md) |
| E4-02 | Hallazgos contextuales fundamentados en recuperación | Generación sin fuentes pierde trazabilidad | Seis reglas limitan cobertura; una cita existente no prueba su interpretación. [RAG](06-rag.md) |
| E4-03 | Separar Ruff/Bandit de Gemini + RAG | Unificar contadores/citas produciría atribuciones falsas | Panel y JSON conservan procedencia y estado. [Contrato](10-analisis-estatico.md) |
| E4-04 | Agente supervisado de solo lectura | Ejecución libre o corrección automática amplía riesgo y alcance | Hasta cuatro pasos totales en v2; revisor principal solicita tres. Sin ejecutar código de entrada. [Agente](08-agente.md) |
| E4-05 | Agente en código y `.py`; ZIP/GitHub directos | Agente por archivo multiplicaría llamadas y tiempo | No afirmar planificación agéntica para proyectos completos. [Arquitectura](03-arquitectura.md) |
| E4-06 | Frontend/backend en un contenedor y dominio | Hosting separado añade CORS y despliegues coordinados | API relativa, build multi-stage, una réplica y volumen. [Despliegue](despliegue.md) |
| E4-07 | Conservar evidencia útil con estado parcial | Un error total descartaría resultados estáticos obtenidos | Sin mensaje de aprobación ni citas inventadas. [Resiliencia](11-resiliencia-gemini.md) |
| E4-08 | Limitar entradas, tasa, concurrencia y salida estática | URL ilimitada expone cuota y recursos | Controles por proceso, no cuotas por persona. Captura acotada no limita toda la memoria. [Pruebas](08-pruebas.md) |
| E4-09 | Avisar del uso de IA y minimizar datos | Enviar material privado sin informar contradice el alcance académico | Aviso de envío a Gemini y exclusión de secretos; no prometer retención no verificada. [Datos](tratamiento-datos.md) |
| E4-10 | Evidencia separada por revisión, proveedor y entorno | Mezclar mocks, demo y producción falsea conclusiones | Mocks validan contratos, no precisión. [Comparación](18-comparacion-semanas-3-4.md) |
| E4-11 | Configuración centralizada en `backend/app/config/` y política `severidad.yaml` | Dispersar reglas dificulta revisar límites y reproducir resultados | Variables sensibles solo en entorno; parámetros efectivos por corrida. [README](../README.md) |
| E4-12 | Actualizar documentos sin fabricar historia | Entrevistas o aprobaciones retrospectivas falsearían procedencia | Mantener pendientes reales de Semana 1. [Cierre documental](19-cierre-documental.md) |

## Confirmación de acciones

Hay dos autorizaciones distintas. El presupuesto ZIP/GitHub vincula una sesión,
instantánea y hash antes de consumir Gemini. Preparar un repositorio sí consulta
GitHub para obtener su contenido. La confirmación de corrección autoriza solo la
descarga del texto revisado, nunca su ejecución ni la sobrescritura del original.
Ambos contratos prueban rechazo, caducidad, idempotencia y conflictos.

La severidad derivada se calcula mediante YAML. La herencia requiere una regla
ofrecida, citada, no ambigua y en la línea validada. El backend reconstruye la
auditoría; no acepta que el modelo la declare. Conserva la severidad original y
nunca la reduce. ID y línea no demuestran por sí solos pertinencia semántica.

## E4-13. Ruta de análisis predeterminada — decisión documental para el cierre

**Recomendación técnica (7 de noviembre de 2026):** ofrecer la **ruta directa como predeterminada** y conservar el **agente v2 como alternativa visible y seleccionable** para código pegado y archivos `.py`. Esta decisión se fundamenta en la evaluación pública posterior a `c522c24`, no en una preferencia estética:

| Indicador, veinte casos por ruta | Directa | Agente v2 |
|---|---:|---:|
| Informes completos | 17/20 | 14/20 |
| Informes parciales | 3/20 | 6/20 |
| Latencia media global | 10,34 s | 22,62 s |
| Intentos SDK reportados | 21 | 71 |

En los **13 pares que se completaron en ambas rutas**, F1 fue 1,00 para ambas. Este subconjunto no permite concluir igualdad general ni una mejora del agente. Los tokens globales permanecen desconocidos. Un A/B de la primera decisión tuvo dos cambios en cinco pares comparables, lo que demuestra influencia del contexto, **no** mejora de precisión. Consultar [evaluación final y límites](evidencias/semana-4/postmerge-c522c24-20261107/README.md) y [comparación](18-comparacion-semanas-3-4.md).

**Alcance de esta decisión:** el código documentado en E4-05 todavía describe el agente integrado para entradas de código y `.py`; **esta sección no demuestra que se haya cambiado el comportamiento predeterminado de la interfaz**. La adopción en frontend, su prueba de regresión y la aprobación final del equipo deben verificarse antes de afirmarlo en la sustentación o el portal. Mientras eso no ocurra, comunicarla como **decisión recomendada pendiente de implementación/aceptación**, no como función ya desplegada.

La justificación para conservar el agente como opción es educativa y de trazabilidad (herramientas y decisiones auditables), sin afirmar superioridad general en la evaluación disponible.

## Registro humano de sustentación y ensayo

Se abrió [registro de sustentación del 7 de noviembre](evidencias/semana-4/registro-sustentacion-20261107.md) para consignar únicamente observaciones recibidas y tiempos **realmente medidos**. El plan de diez diapositivas/720 segundos del equipo no acredita ejecución oral ni coincide todavía con el PDF de doce diapositivas versionado. No se llenarán campos con datos supuestos.

## Pendientes de aceptación formal

- Disponibilidad variable y errores 503 observados del proveedor.
- Cobertura limitada, falsos positivos/negativos y revisión humana necesaria.
- Límites por proceso sin identidad de usuario ni coordinación entre réplicas.
- QA-H02: conclusión trazable sobre la credencial histórica, sin reproducirla.
- Instalación automatizada de 5 min 45 s con cachés: falta comprobación humana independiente.
- Consultar la comparación real y su alcance en [docs/18](18-comparacion-semanas-3-4.md).

La aceptación final de riesgos y la autorización de entrega corresponden al equipo.
