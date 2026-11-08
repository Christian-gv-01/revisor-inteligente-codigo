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

## E4-13. Ruta predeterminada del agente — justificación revisada para cierre

**Revisión documental del 8 de noviembre de 2026:** se opta **provisionalmente por mantener el agente v2 como ruta predeterminada implementada para texto Python y archivos `.py`** y la ruta directa como alternativa. Esto concilia el enrutamiento efectivo de la versión integrada con la decisión que documentó Ronald en `127522e`. La recomendación previa del 7 de noviembre de adoptar la ruta directa se conserva como alternativa razonable, **no como cambio de frontend que se hubiera desplegado**.

| Resultado real, 20 solicitudes por ruta | Ruta directa | Agente v2 |
|---|---:|---:|
| Informes completos | **17/20 (85 %)** | **14/20 (70 %)** |
| Informes parciales | 3/20 | 6/20 |
| Latencia media | **10,34 s** | **22,62 s** |
| Intentos SDK reportados | **21** | **71** |

En los **13 pares con informes completos en ambas rutas**, la F1 fue **1,00** en las dos; por ser un subconjunto seleccionado no demuestra equivalencia general. Los tokens totales son **desconocidos** por metadatos incompletos. La corrida histórica de `8e66b2c` sí encontró peor F1 del agente (0,762) frente a la ruta directa (0,957) en 20 pares completos, pero usó una versión y protocolo distintos.

**Motivo para conservar la ruta del agente:** el alcance académico de CODEGUARD comprende inspección inicial obligatoria, selección de herramientas permitidas, contexto, referencias y trazabilidad de cada decisión. Mantenerlo visible en el recorrido principal permite demostrar y evaluar esa orquestación supervisada con resultados y límites verificables. **No es una decisión sustentada en precisión superior, latencia inferior ni ahorro de consumo**: los datos observados favorecen a la ruta directa en completitud, tiempo e intentos.

**Riesgo aceptado provisionalmente:** mayor probabilidad de resultado parcial y espera. La alternativa directa debe permanecer accesible y claramente identificada. No se declara mejora hasta medirla en un conjunto nuevo con configuración congelada y revisión independiente de citas. Proponer en futuros trabajos un selector explícito de ruta y considerar la directa como predeterminada si el criterio principal pasa a ser completitud y rapidez.

**Estado de aprobación:** justificación técnica escrita e integración documental; no sustituye el acuerdo expreso del equipo ni evidencia un cambio de comportamiento del frontend. [Resultados y limitaciones](evidencias/semana-4/postmerge-c522c24-20261107/README.md); [comparación histórica](18-comparacion-semanas-3-4.md).

## Registro humano de sustentación y ensayo

Se abrió [registro de sustentación del 7 de noviembre](evidencias/semana-4/registro-sustentacion-20261107.md) para consignar únicamente observaciones recibidas y tiempos **realmente medidos**. El equipo comunicó una **duración total cronometrada de 600 segundos (10 minutos)** frente a los 720 segundos planificados. El [PDF final ya versionado](presentacion/README.md) contiene **12 diapositivas**; la distribución anterior de 10 y los tiempos individuales siguen siendo planificación histórica. Se registró la **retroalimentación escrita** del docente del 8 de noviembre; faltan observaciones orales adicionales, si existieron, y confirmar el archivo proyectado durante la medición.

## Pendientes de aceptación formal

- Disponibilidad variable y errores 503 observados del proveedor.
- Cobertura limitada, falsos positivos/negativos y revisión humana necesaria.
- Límites por proceso sin identidad de usuario ni coordinación entre réplicas.
- QA-H02: conclusión trazable sobre la credencial histórica, sin reproducirla.
- Instalación automatizada de 5 min 45 s con cachés: falta comprobación humana independiente.
- Consultar la comparación real y su alcance en [docs/18](18-comparacion-semanas-3-4.md).

La aceptación final de riesgos y la autorización de entrega corresponden al equipo.
