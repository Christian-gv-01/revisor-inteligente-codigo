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

## Pendientes de aceptación formal

- Disponibilidad variable y errores 503 observados del proveedor.
- Cobertura limitada, falsos positivos/negativos y revisión humana necesaria.
- Límites por proceso sin identidad de usuario ni coordinación entre réplicas.
- QA-H02: conclusión trazable sobre la credencial histórica, sin reproducirla.
- Instalación automatizada de 5 min 45 s con cachés: falta comprobación humana independiente.
- Consultar la comparación real y su alcance en [docs/18](18-comparacion-semanas-3-4.md).

La aceptación final de riesgos y la autorización de entrega corresponden al equipo.

## E4-13: Directa predeterminada y Agente opcional

Decisión de producto aprobada por Christian el 7 de noviembre de 2026, al responder
la revisión docente del mismo día. En modo API, código pegado y .py comienzan en
Directa. Agente queda como opción visible para revisar planificación y trazabilidad.
Cambiar de ruta limpia el resultado y la propuesta visibles y no inicia análisis.
ZIP/GitHub conservan su flujo directo y el presupuesto previo obligatorio.

Motivo: la corrida exploratoria c522c24 completó 17/20 informes directos frente a
14/20 del agente, con medias globales 10,34/22,62 s e intentos SDK 21/71. No se
demostró mejora de precisión; el F1 1,0 de trece pares completos no se extiende
a los veinte. Los tokens totales permanecen desconocidos y la huella del índice
se observó durante y al final, no antes. La decisión responde al resultado
observado, sin afirmar superioridad universal ni repetir llamadas para elegir
una corrida favorable. El planificador y los contratos no cambian.

Alternativa descartada como predeterminada: mantener el agente obligatorio solo
para destacar sus herramientas académicas. Se conserva el acceso explícito para
ese propósito y se informa que puede requerir más llamadas y tiempo.

Validación: selección inicial Directa para texto y .py, endpoints reales del
backend con SDK simulado, ninguna planificación automática, selección explícita
de Agente y regresiones de su traza, presupuesto y correcciones. Evidencias en
[revisión 7](evidencias/semana-4/revision7-cierre-20261107/). Se mantienen los JSON
reales de c522c24; el selector no modifica sus métricas ni acredita una nueva
evaluación generativa.
