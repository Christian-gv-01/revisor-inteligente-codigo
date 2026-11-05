# Auditoría de entrega e integración de CODEGUARD

Fecha: 5 de noviembre de 2026, America/Guayaquil.
Revisión auditada: `c2b9b06a10735cd21b0b623679f521e8b8a5ab60` de `main`.

Fuente de requisitos: [portal de entregas del seminario](https://fabig76.github.io/entregas-ia-uniandes/), consultado directamente como HTML el 5 de noviembre. La lista se genera desde el JavaScript de la página. La captura facilitada por Christian añade el marco general: web, modelo generativo, conocimiento propio, agente especializado, Git y nube.

## Dictamen

La plataforma cumple los seis componentes generales mediante implementaciones y evidencias concretas. Esto **no equivale a tener completa toda la entrega**. Faltan documentos exigidos, comparación final de calidad y presentación, y la integración del agente con el producto principal es incompleta.

Las 230 pruebas backend y 26 escenarios públicos acreditan sus aserciones; no miden exhaustividad de detección de vulnerabilidades. Menos hallazgos no demuestra automáticamente mayor precisión.

La página fija la sustentación para el sábado 7 de noviembre y la entrega final para el lunes 9 de noviembre de 2026 a las 23:59, con prórroga al miércoles 11. Las observaciones de sustentación solo podrán documentarse después de que ocurra.

## 1. Componentes generales

| Componente | Resultado | Evidencia y límite |
|---|---|---|
| Web | Implementado | React en la raíz y API pública; el modo inicial de React es demo |
| Modelo | Implementado | Gemini en servicio encapsulado, JSON validado, ejecuciones reales guardadas |
| Conocimiento | Implementado, cobertura limitada | Seis reglas curadas con enlaces oficiales; ChromaDB persistente |
| Agente | Implementado, integración parcial | Planificación real, tres pasos máximos, herramientas AST; principal y Agent Lab son flujos diferentes |
| Git | Implementado | Cambios, revisiones y evidencias versionados; falta validar correspondencia de cuentas con los tres integrantes |
| Nube | Implementado | Railway, salud y endpoint estático; continuidad de citas y log del reinicio |

## 2. Entrega 4: lista completa de 14 obligatorios

Esta matriz es una revisión del repositorio, no una selección enviada al portal. “Pendiente” incluye lo que no aparece en la revisión auditada; no demuestra ausencia en el computador de otro integrante.

| ID | Punto | Estado | Comprobación |
|---|---|---|---|
| s4a | URL y salud | Comprobado | README y /health público |
| s4b | Secretos | Parcial | Configuración privada prevista y errores protegidos; el reporte histórico de auditoría requiere revisión. Falta registrar la conclusión del fixture P26 y una auditoría final de historial |
| s4c | Índice | Comprobado con alcance | Antes/después: analizado, un hallazgo, mismas tres fuentes y log de recuperación. No certifica integridad completa del volumen |
| s4d | Pruebas públicas | Parcial de alcance | 26/26 y docs/08-pruebas.md; P26 usa AST local. No acredita resistencia del Gemini real a instrucciones en documentos |
| s4e | Comparación final | Pendiente | Hay recuperación de semana 3 y A/B de decisiones, pero no comparación final equivalente de calidad del revisor |
| s4f | Tasa y errores | Implementado y probado en escenarios | Límites y mensajes seguros; no extrapolar a cuotas distribuidas o identidad individual detrás del proxy |
| s4g | Aviso y datos | Implementado | PrivacyNotice y limitaciones documentadas |
| s4h | Instalación y ADR | Parcial | README/ADR existen; no se ha evidenciado instalación limpia cronometrada en diez minutos. Arquitectura/decisiones contienen estados históricos |
| s4i | Aportes e IA | Parcial | Documento presente con cuentas/roles ambiguos; debe validarlo el equipo |
| s4j | PDF | Pendiente | No hay PDF de sustentación bajo docs/ en el árbol auditado |
| s4k | Evidencias | Parcial por fecha | Despliegue, CI, pruebas y reinicio presentes; las observaciones de sustentación aún no han ocurrido |
| c-zip | Paquete | No verificado | No se creó ni revisó el ZIP final. Nombre esperado según el proyecto registrado: CODEGUARD_Semana4.zip; máximo 20 MB |
| c-sec | Limpieza del paquete | No verificado | Se debe inspeccionar el ZIP real: sin .env, entornos, dependencias, cachés ni secretos |
| c-git | Correspondencia | Parcial | Falta comparar contenido del ZIP con la revisión de entrega y validar participación semanal de los tres integrantes |

## 3. Revisión de semanas anteriores

Los puntos comunes del paquete se repiten en cada semana. Se revisan aquí los puntos específicos sin afirmar que ya se entregaron archivos al portal.

### Semana 1

| ID | Punto | Estado y evidencia |
|---|---|---|
| s1a | Propuesta | Parcial: docs/01-propuesta.md; identifica Gemini pero falta justificar de forma concreta el modelo y sus alternativas |
| s1b | Historias | Incompleto: docs/02-requisitos.md contiene tablas RF/RS/RNF, no ocho historias con Dado/Cuando/Entonces |
| s1c | Arquitectura | Parcial: diagrama inicial e histórico; falta topología vigente con agente, herramientas y RAG |
| s1d | Fuentes | Falta docs/04-fuentes.md |
| s1e | Levantamiento | No localizado: los 20 casos sintéticos de evaluación no prueban una entrevista o levantamiento real |
| s1f | Materia prima | No existe data/raw/; knowledge/ contiene resúmenes y enlaces. Falta el inventario explícito de documentos/enlaces admitidos por el requisito |
| s1g | Base del repo | README, .gitignore y .env.example presentes |
| s1h | Evidencias iniciales | No aparece docs/evidencias/semana-1/ |
| s1i | Salud local | Funcionalidad acreditada posteriormente; este punto es opcional en la página |

No se deben fabricar retrospectivamente entrevistas, actas o capturas semanales. Las faltas históricas se explican al docente.

### Semana 2

| ID | Punto | Estado y evidencia |
|---|---|---|
| s2a | Endpoint tipado | Implementado: FastAPI y modelos |
| s2b | Cliente LLM | Implementado: app/services/llm.py |
| s2c | Tres prompts | Archivos V1/V2/V3 y resultados de diez casos |
| s2d | Comparación | Evidencia de 30 solicitudes y tabla de versiones; conviene hacer visible la clasificación por entrada exigida por la guía. El script backend/scripts/probar_analisis.py citado por el documento no aparece en el árbol actual |
| s2e | Interfaz | Implementada, con carga y errores |
| s2f | Clave privada | Protección de .env; verificar historial final, no solo archivos actuales |
| s2g | Fallos del proveedor | Parcial: timeout/vacío y reintento 502/503/504. El 429 se convierte en 503 y no está en la lista de reintentos, a diferencia de la guía |
| s2h | Telemetría | Parcial: informe final registra tokens/tiempo; no hay medición completa de tokens de todas las llamadas del planificador |
| s2i | Modelo simulado | Implementado en tests |
| s2j | C4 y ADR | Parcial: documentos con estado histórico y decisiones todavía “propuestas” |
| s2k | Evidencias | Presentes, distinguiendo alcance de cada ejecución |

### Semana 3

| ID | Punto | Estado y evidencia |
|---|---|---|
| s3a | Ingesta | Implementada: limpieza, secciones, embeddings, metadatos; no inventa vigencia |
| s3b | Fragmentación | Documentada en docs/06-rag.md |
| s3c | Citas | Implementadas y resueltas por archivo/ID |
| s3d | Abstención | Implementada y probada; su granularidad actual puede eliminar hallazgos válidos junto a uno inválido |
| s3e | Herramientas | Parcial: selección tipada y límite; resultados de herramientas siguen siendo dict genérico, no modelos específicos por herramienta |
| s3f | Configuración | Parcial: variables de entorno para varios valores, pero no config/ y existen límites fijos en código; justificar o alinear al formato solicitado |
| s3g | Confirmación | No aplica a los flujos actuales de solo lectura; documentar expresamente que no envía, registra ni deriva acciones externas. Si se agregan, requieren confirmación |
| s3h | Evaluador | Presente: 20 casos y run_eval.py |
| s3i | Calidad | Recuperación real de semana 3; calidad generativa completa y comparación final pendientes |
| s3j | Tests | Implementados para herramientas, planificación y construcción segura del prompt |
| s3k | Evidencias | Presentes; pruebas simuladas de inyección no equivalen a robustez general del modelo real |

## 4. Por qué pueden verse menos errores

### Comprobaciones directas en el código

1. **Demo y API tienen distinto alcance.** HomePage.tsx inicia con modo demo. La demo usa reglas ilustrativas; no ejecuta Gemini ni RAG. Comparar sus conteos con API real no es una evaluación.
2. **Ruff no está configurado como linter exhaustivo.** Solo selecciona E4, E7, E9 y F; otras familias de estilo no se buscan. Bandit busca otro conjunto de patrones.
3. **La cobertura documental es pequeña.** knowledge/seguridad_python.md contiene seis reglas. El informe contextual exige citas recuperadas; no es una revisión completa de todos los errores Python.
4. **Una búsqueda recupera tres fragmentos.** _recuperar_contexto_rag invoca buscar_fragmentos(..., limite=3). Un archivo con varias categorías puede necesitar fuentes de más categorías. Es un riesgo de cobertura a evaluar, no un fallo probado para cualquier entrada.
5. **La validación es global.** En llm.py, una referencia ausente o inválida en un solo hallazgo hace retornar un informe abstenido para todo el resultado. Los otros hallazgos válidos también desaparecen de esa respuesta.
6. **Hay fallos reales 503.** El respaldo estático conserva alertas, pero el informe contextual parcial puede tener cero hallazgos. Eso significa revisión incompleta.
7. **Los contadores están separados.** FindingsPanel cuenta solo result.hallazgos; las observaciones Ruff/Bandit aparecen debajo y sus líneas no forman parte de los markers contextuales del editor.
8. **El prompt activo es V1.** llm.py fija system_v1.md; tener V2/V3 en el repo no significa que estén activas.
9. El máximo de salida predeterminado es 2048 tokens. Podría limitar informes extensos; no se atribuye una pérdida concreta a truncamiento sin examinar su respuesta y motivo de terminación.

**Lo que no puede concluirse todavía:** que la última corrección de captura haya causado una regresión, que el modelo sea peor o que bajar el conteo sea una mejora. Falta el mismo fragmento, modalidad, configuración y respuesta anterior para comparar.

### Cómo medirlo

Congelar el conjunto de 20 casos y sus etiquetas antes de cambiar la lógica. Separar:
- calidad contextual: TP, FP, FN, precisión, recall, F1 y abstenciones;
- herramientas: reglas y estados de cada motor;
- servicio: errores, completitud, latencia y tokens;
- fuentes: recuperación, referencias resueltas y pertinencia revisada.

La semana 3 midió recuperación: Recall@3 0,9444 y Precision@3 0,5370 sobre 18 casos etiquetados. No son métricas de hallazgos Gemini. El A/B de seis casos evaluó una primera decisión: cinco pares comparables y cero cambios. No prueba mayor detección del agente. No se deben comparar esas cifras como si midieran la misma variable.

## 5. Integración real del agente

### Estado observado

- React llama a analyzeCode y a /analizar, /archivos, /archivos/zip o /repositorios/github. No llama a /agente/analizar.
- Agent Lab es otra página HTML y otro endpoint.
- El agente ejecuta Ruff/Bandit y proporciona un resumen al planificador. Los pasos previos sí pueden influir en la siguiente selección de herramienta.
- El planificador elige entre herramientas de una lista cerrada. No es una ejecución de código arbitrario.
- **Al terminar, ejecutar_agente llama a analizador(solicitud.codigo). No entrega pasos, decisiones ni hallazgos estáticos al generador del informe final.**
- Por ello, el planificador y las herramientas funcionan, pero su evidencia no participa directamente en esa síntesis final. No se ha demostrado que aumenten la calidad de los hallazgos.

### Diseño recomendado para un solo producto

Una interfaz principal, un contrato de análisis y un coordinador común por archivo:

1. Validar la entrada y obtener sus archivos mediante los validadores existentes.
2. Ejecutar Ruff/Bandit obligatorios y construir evidencia tipada, limitada y con procedencia.
3. Planificación supervisada: decidir inspecciones AST que aporten información; permitir finalizar temprano y conservar el límite.
4. Ejecutar esas herramientas y añadir sus resultados al contexto de la siguiente decisión.
5. Recuperar documentación pertinente a las categorías observadas, con presupuesto explícito de fuentes y sin convertir reglas estáticas en citas.
6. Generar el informe final usando código, documentación y evidencia de herramientas como datos no confiables separados de las instrucciones.
7. Validar el resultado y presentar un informe común con fuentes, traza y estado real. Un fallo parcial no debe parecer una aprobación de seguridad.

El mismo coordinador debe ser reutilizado por código pegado y archivo Python. ZIP/GitHub deben coordinar archivos con presupuesto global de solicitudes y tiempo; no multiplicar sin control tres llamadas por cinco archivos. Se puede integrar por etapas, identificando con claridad qué modalidades usan ya el agente.

Agent Lab puede conservarse como vista técnica de la misma ejecución; no necesita ser un segundo producto ni iniciar otro análisis para mostrar una traza.

### Valor que debe aportar y poder demostrarse

| Parte | Aporte comprobable |
|---|---|
| Ruff/Bandit | Inspección reproducible y respaldo cuando falla el proveedor |
| Herramientas AST | Información estructurada para comprobar patrones concretos |
| Planificador | Elegir inspecciones según evidencia y detener las innecesarias |
| RAG | Recuperar documentación trazable que sustente la interpretación |
| Síntesis final | Relacionar código y evidencia, priorizar y explicar correcciones |
| Interfaz | Mostrar el resultado, sus límites y la traza sin cambiar de aplicación |

La procedencia debe seguir separada en los datos, aunque el producto sea uno. No sumar una alerta Bandit y un hallazgo Gemini sobre la misma consulta y llamarlos automáticamente “dos vulnerabilidades”. Hasta tener una regla explícita de equivalencia, mostrar conteos claros de hallazgos contextuales y observaciones de herramientas.

## 6. Contratos y aceptación propuestos

Estas son tareas pendientes, no funcionalidades declaradas como terminadas.

- Resultado común por archivo con informe, fuentes, analisis_estatico y traza opcional; estados analizado, abstenido y parcial con motivo.
- Modelos de evidencia específicos para estructura, llamadas sensibles y SQL, con límites, archivo/línea, origen y estado.
- El generador final recibe la evidencia validada sin ejecutar código, obedecer texto no confiable ni inventar citas.
- Tests prueban que la evidencia realmente llega a la síntesis y que el reporte/traza corresponden a una sola ejecución.
- Si una cita falla, definir y probar un contrato de revisión parcial que preserve lo verificable y explique lo rechazado; no cambiarlo sin tests porque actualmente la abstención es global.
- Medir el mismo conjunto antes/después. No escoger ejemplos retrospectivamente para favorecer al agente.
- Aceptación visual: entrada, decisiones, resultado, fuentes y exportación disponibles en la interfaz principal; errores y degradación visibles.

## 7. Prioridad de trabajo

1. Integrar evidencia del agente en la síntesis y exponer la ejecución en el frontend principal, empezando por código/.py con contratos y regresiones.
2. Medir cobertura de los ejemplos anteriores y de los 20 casos congelados; revisar recuperación y abstención por hallazgo con base en falsos negativos reales.
3. Completar inventario de fuentes, historias de usuario y arquitectura/ADR vigentes. No fabricar el levantamiento ni evidencias históricas.
4. Repetir evaluación comparable tras congelar la implementación; registrar errores y revisión humana.
5. Preparar presentación de 12 minutos, validar tabla de integrantes y crear ZIP final limpio de hasta 20 MB.
6. Incorporar observaciones reales de la sustentación y emitir la matriz final de entrega.

No hace falta añadir funciones comerciales, corrección automática o ejecución de código para satisfacer estos puntos.

## 8. Alcance de esta auditoría

Se inspeccionaron la lista del portal y el árbol/código/documentación de la revisión indicada. Se reutilizaron resultados existentes de CI y producción sin presentarlos como nuevas ejecuciones de IA. No se evaluaron nuevamente 20 respuestas generativas ni se comprobó el contenido de un ZIP final. Este documento es un diagnóstico y plan de integración; no acredita que las tareas propuestas ya estén implementadas.

## 9. Comparación autorizada con muestra_vulnerable.py

Después de esta auditoría, Christian aportó el archivo de prueba y autorizó explícitamente enviarlo a Railway y Gemini. Se hicieron una solicitud normal y una de agente con el mismo contenido y nombre. [Resultados estructurados](evidencias/semana-4/comparacion-muestra-20261105/resultados.json).

SHA-256 del código: `9a363f3fb3afec5b02b2fa45b508c18d92dc069e89d80a12896f04c71eb74090`. Tiene 49 líneas. Se omite el código fuente en la evidencia y se conservan los informes contextuales, reglas/líneas estáticas y la traza; no se almacenan textos de alertas estáticas que reproduzcan el valor ficticio de prueba.

| Resultado | Normal | Agente |
|---|---:|---:|
| HTTP | 200 | 200 |
| Estado contextual | analizado | analizado |
| Hallazgos contextuales | 2 | 2 |
| Ruff | 4 | 4 |
| Bandit | 11 | 11 |
| Observaciones estáticas combinadas | 15 | 15 |
| Fuentes recuperadas | 002, 001, 004 | 002, 001, 004 |
| Tiempo HTTP observado | 12.970 ms | 16.375 ms |

Los IDs abreviados llevan prefijo `seguridad_python-`. La recuperación no incluyó la regla 003 de comandos, aunque el archivo contiene una llamada con shell=True y la herramienta AST del agente localizó `subprocess.call` en línea 21. La síntesis final de ambos flujos solo reportó SQL y eval. La alerta estática B602 sí se conservó. Esto distingue pérdida de cobertura contextual de pérdida de observaciones del motor estático.

### Defecto reproducido de ubicación

La llamada eval está en línea **25**. El flujo normal indicó **24** (definición de función) y el agente **27** (línea vacía). La construcción SQL fue señalada correctamente en la 16. La validación de límites de línea no comprueba correspondencia entre el hallazgo y la instrucción concreta.

La herramienta AST del propio agente sí devolvió eval en línea 25, pero ese resultado no se transmite al generador final. Debe integrarse evidencia con ubicación verificable en la síntesis, mejorar la representación numerada del código y probar el anclaje entre cada hallazgo y su fragmento. No basta con aceptar cualquier número de línea dentro del archivo.

### Caso adicional fuera de las reglas seleccionadas

Una comprobación local específica con Ruff B006 detectó la lista mutable predeterminada en línea 47. B006 no pertenece a E4,E7,E9,F. Es una falta de cobertura de la configuración actual, no una desaparición de una observación generada por esas reglas.

### Conclusión de esta ejecución

No se observó una caída de las 15 observaciones estáticas entre ambos flujos. No hubo ganancia de cobertura contextual en esta muestra; el agente reportó las mismas dos categorías, con peor ubicación de eval en esta ejecución. Es una pareja, no una estimación estadística ni una comparación con la versión histórica anterior.

Prioridades concretas: transmitir la evidencia tipada a la síntesis, recuperar documentación para las categorías detectadas, verificar la ubicación de hallazgos y mostrar en una interfaz común los estados y conteos por procedencia. Después medir de nuevo sobre el conjunto congelado y este archivo.
