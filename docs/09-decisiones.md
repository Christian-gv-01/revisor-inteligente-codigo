# 09. Decisiones técnicas y éticas

> Ampliación local del 6 de noviembre: se propone aprobar únicamente la descarga
> de una copia, tras revisar la propuesta. No se autoriza ejecución ni modificación
> automática por el agente. El [contrato](20-contrato-confirmacion-humana.md) sigue
> pendiente de acuerdo con Backend y su adaptador real permanece deshabilitado.

Consolidación: 5 de noviembre de 2026, base `65675e2`.
Responsables: Christian Gamboa (Backend, IA, agente y despliegue), Andy (Frontend
y evaluación), Ronald Yépez (QA, seguridad y documentación).

Este registro describe decisiones implementadas y su justificación; no es un acta
de aprobación grupal. Se conserva el [registro de revisión 2](historico/09-decisiones-revision2.md).
Los identificadores E4 no reemplazan sus ADR históricos.

| ID | Decisión implementada | Alternativa y motivo | Consecuencia / verificación |
|---|---|---|---|
| E4-01 | Gemini encapsulado y modelo configurable | Cambiar de proveedor exige adaptador y nueva evaluación; solo estático no aporta síntesis RAG | Depende de cuota y disponibilidad; sin fallback Groq. [Propuesta](01-propuesta.md) |
| E4-02 | Hallazgos contextuales fundamentados en recuperación | Generación sin fuentes pierde trazabilidad | Seis reglas limitan cobertura; una cita existente no prueba su interpretación. [RAG](06-rag.md) |
| E4-03 | Separar Ruff/Bandit de Gemini + RAG | Unificar contadores/citas produciría atribuciones falsas | Panel y JSON conservan procedencia y estado. [Contrato](10-analisis-estatico.md) |
| E4-04 | Agente supervisado de solo lectura | Ejecución libre o corrección automática amplía riesgo y alcance | Hasta tres inspecciones; sin ejecutar código de entrada. [Agente integrado](17-agente-integrado.md) |
| E4-05 | Agente en código y `.py`; ZIP/GitHub directos | Agente por archivo multiplicaría llamadas y tiempo | No afirmar planificación agéntica para proyectos completos. [Arquitectura](03-arquitectura.md) |
| E4-06 | Frontend/backend en un contenedor y dominio | Hosting separado añade CORS y despliegues coordinados | API relativa, build multi-stage, una réplica y volumen. [Despliegue](despliegue.md) |
| E4-07 | Conservar evidencia útil con estado parcial | Un error total descartaría resultados estáticos obtenidos | Sin mensaje de aprobación ni citas inventadas. [Resiliencia](11-resiliencia-gemini.md) |
| E4-08 | Limitar entradas, tasa, concurrencia y salida estática | URL ilimitada expone cuota y recursos | Controles por proceso, no cuotas por persona. Captura acotada no limita toda la memoria. [Pruebas](08-pruebas.md) |
| E4-09 | Avisar del uso de IA y minimizar datos | Enviar material privado sin informar contradice el alcance académico | Aviso de envío a Gemini y exclusión de secretos; no prometer retención no verificada. [Datos](tratamiento-datos.md) |
| E4-10 | Evidencia separada por revisión, proveedor y entorno | Mezclar mocks, demo y producción falsea conclusiones | Mocks validan contratos, no precisión. [Comparación](18-comparacion-semanas-3-4.md) |
| E4-11 | Variables de entorno y límites fijos versionados | Carpeta `config/` es otra organización no implementada | Documentar valores efectivos y variables heredadas sin consumidor. [README](../README.md) |
| E4-12 | Actualizar documentos sin fabricar historia | Entrevistas o aprobaciones retrospectivas falsearían procedencia | Mantener pendientes reales de Semana 1. [Cierre documental](19-cierre-documental.md) |

## Confirmación de acciones

El producto inspecciona y devuelve resultados; no envía correos, crea PR, modifica
repositorios o aplica correcciones por decisión del modelo. No hay una escritura
externa que requiera confirmación del agente. Si se incorpora, deberá diseñarse
aprobación explícita y probarse antes de habilitarla. Esto no elimina el aviso del
envío de código al proveedor.

## Pendientes de aceptación formal

- Disponibilidad variable y errores 503 observados del proveedor.
- Cobertura limitada, falsos positivos/negativos y revisión humana necesaria.
- Límites por proceso sin identidad de usuario ni coordinación entre réplicas.
- QA-H02: conclusión trazable sobre la credencial histórica, sin reproducirla.
- Instalación en diez minutos y comparación generativa equivalente sin evidencia final.

La aceptación final de riesgos y la autorización de entrega corresponden al equipo.

## Justificación de la ruta predeterminada del agente

### Decisión adoptada

Se mantiene provisionalmente el agente supervisado como ruta predeterminada para código pegado y archivos `.py`. La ruta directa permanece disponible como alternativa.

### Resultados de la evaluación comparativa

La evaluación consideró 20 casos:

| Indicador | Agente supervisado | Ruta directa |
|---|---:|---:|
| Informes completos | 14/20 (70 %) | 17/20 (85 %) |
| Latencia | Aproximadamente 2 veces mayor | Referencia |
| Intentos SDK | Aproximadamente 3,4 veces más | Referencia |

La ruta directa obtuvo tres informes completos adicionales, equivalentes a una diferencia de 15 puntos porcentuales.

### Justificación

Se conserva provisionalmente el agente como ruta predeterminada por su función de inspección contextual supervisada, recuperación de información y análisis fundamentado en evidencias.

Esta decisión responde al alcance funcional de CODEGUARD, no a una superioridad de rendimiento demostrada. Los resultados comparativos muestran que la ruta directa consiguió mayor completitud y menor latencia.

Cuando se prioricen rapidez y completitud, la ruta directa constituye una alternativa válida.

### Limitaciones

La evaluación disponible no permite concluir cuál ruta tiene mayor precisión, menor tasa de falsos positivos, mejor cobertura de vulnerabilidades o mayor validez de referencias documentales.

Tampoco se dispone del total de tokens consumidos ni de la huella del índice utilizada antes de la ejecución. Por tanto, no se afirma ahorro de tokens ni reproducibilidad completa.

### Validación futura

Se recomienda repetir los mismos 20 casos bajo condiciones equivalentes y registrar:

- Huella del índice y configuración utilizada.
- Informes completos.
- Latencia.
- Tokens consumidos.
- Intentos SDK.
- Precisión y falsos positivos.
- Validez de las referencias y evidencias.

La decisión deberá revisarse con esos resultados y con los criterios de aceptación del equipo.

### Alcance de la actualización

Esta justificación es documental. No modifica el enrutamiento, la configuración ni el código fuente del agente. La ruta predeterminada efectiva continúa siendo la implementada en la versión revisada.
