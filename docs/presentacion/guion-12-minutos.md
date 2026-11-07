# Guion de doce minutos: cierre documental y presupuesto

Base: `467d00e0d56a98cd758f382a5c713737eb490845`. Preparación del 7 de noviembre de 2026. Duración planificada: 720 segundos; no es un ensayo cronometrado. Reparto y preguntas sujetos a las indicaciones del ingeniero. Comparación final pendiente.

## 1. CODEGUARD

Tiempo: 30 segundos.

Presentamos CODEGUARD, revisión asistida de Python con herramientas estáticas, recuperación documental y un agente supervisado. Esta preparación parte de 467d00e, integración del PR 48. Ronald consolidó la documentación y revisó el consentimiento de proyectos. Las métricas históricas conservan su versión. Christian entregará la comparación final de los mismos veinte casos. No afirmamos una mejora de precisión del agente. El reparto y el tiempo real requieren acuerdo y ensayo del equipo.

Fuentes: docs/08-agente.md; docs/evidencias/semana-4/cierre-agente-presupuesto-20261107/README.md

## 2. Una revisión útil necesita evidencia

Tiempo: 60 segundos.

Explicar el problema con una consulta SQL construida por concatenación. El producto ayuda a localizar el patrón y a entender la recomendación. No afirmar que reemplaza una auditoría ni que cualquier alerta sea explotable. El valor esperado es facilitar revisión y trazabilidad; no tenemos una medición con usuarios que cuantifique tiempo ahorrado. Separar valor esperado de resultados medidos.

Fuentes: docs/01-propuesta.md

## 3. Del código al informe

Tiempo: 60 segundos.

La arquitectura integra entrada validada, Ruff/Bandit y AST, recuperación documental y síntesis. Para código pegado y .py el frontend solicita agente v2. Las decisiones pueden ampliar una ventana de código, buscar una referencia por categoría permitida o finalizar. El límite es tres pasos totales, dos decisiones y una síntesis, con hasta nueve intentos Gemini y plazo cooperativo de 150 segundos. ZIP y GitHub siguen el análisis directo por archivo. Su consentimiento de presupuesto es un recorrido separado y está apagado por defecto. La fusión de PR 48 no acredita la revisión que está activa en Railway.

Fuentes: docs/08-agente.md; docs/contrato-agente-v2/README.md

## 4. El recorrido del agente v2

Tiempo: 70 segundos.

En el panel del agente se ve qué herramientas se ejecutaron y de dónde procede la decisión. Ampliar contexto devuelve una ventana acotada del código original. Buscar referencia usa categorías permitidas y el índice local, sin visitar enlaces. Los resultados se propagan a la decisión siguiente y a la síntesis. La interfaz no muestra una decisión fallida como un resultado exitoso y conserva el respaldo local identificado. Finalización anticipada y herramienta repetida explican por qué cesaron las inspecciones, sin prometer cobertura completa. El JSON conserva la traza. El renderizado trata código y documentos como texto y mantiene las URLs documentales sin enlaces activos.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45; frontend/src/components/AgentTracePanel.tsx; frontend/tests/agent-v2.test.tsx

## 5. La aprobación ocurre después de revisar

Tiempo: 70 segundos.

El contrato v1 ya está integrado. La previsualización permite comparar original y propuesta antes de tomar una decisión. La casilla comienza desmarcada y aprobar únicamente autoriza descargar la copia revisada. Sesión, identificador, hashes y caducidad vinculan la decisión a una propuesta concreta. El frontend verifica que la respuesta coincida con el contenido mostrado. Cancelar o cambiar la entrada invalida el consentimiento y descarta respuestas tardías. No se ejecuta el código ni se sobrescriben originales. El PR 37 registra además aprobación, idempotencia, rechazo y conflictos mediante HTTP con propuestas reales. La caducidad y el flujo visual corresponden a CI controlado con Gemini simulado.

Fuentes: docs/23-integracion-confirmacion-qa.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 6. Presupuesto de análisis ZIP y GitHub

Tiempo: 70 segundos.

Este consentimiento autoriza analizar un proyecto, no descargar una corrección. La previsualización guarda contenidos y muestra el presupuesto antes de llamar a Gemini. GitHub sí se consulta para preparar los archivos. La casilla comienza desmarcada y aprobar vincula sesión, identificador y hash a la instantánea. Se admiten hasta cinco Python, doce mil caracteres combinados y ZIP de hasta cinco MB. Hay hasta tres intentos por archivo, máximo quince por proyecto y plazo cooperativo de hasta 150 segundos. Los valores efectivos los devuelve Backend. Rechazar o cambiar la entrada antes de aprobar no autoriza consumo. Después de aprobar, dejar de esperar solo interrumpe el navegador. El modo Demo es una simulación separada. No activar la función en producción durante la exposición. Se verificaron los archivos, análisis previstos, máximo de intentos y plazo cooperativo en ambos tipos de entrada. Ese plazo es un límite, no una predicción de duración. Aprobar permitió llamadas al proveedor simulado; rechazar y caducar no añadieron llamadas. También se comprobó el bloqueo visual por vencimiento. Estas pruebas aisladas no habilitaron el presupuesto publicado.

Fuentes: docs/28-presupuesto-proyectos.md; docs/evidencias/semana-4/cierre-agente-presupuesto-20261107/README.md

## 7. El informe comunica sus límites

Tiempo: 60 segundos.

La integración del PR 48 incluye pesos de severidad 8, 4, 2 y 1 y factores de confianza de Bandit 1,0, 0,8 y 0,6. Son ponderaciones operativas, no probabilidades. Se conserva la severidad original y su dominancia, con desempates por categoría y orden estable. Si falta confianza reconocida no hay puntuación. El informe de IA no hereda la confianza de Bandit. El frontend conserva el orden y muestra bandas de severidad. Un estado parcial indica que no se completó el análisis, aunque conserve hallazgos útiles. Esta política no demuestra mayor precisión del agente.

Fuentes: docs/10-analisis-estatico.md; docs/31-validacion-conjunta-pr46-pr47.md

## 8. Referencia histórica con Gemini real

Tiempo: 60 segundos.

El PR 37 conserva una corrida real del endpoint de análisis sobre veinte casos congelados. Completaron los veinte informes, sin respuestas parciales ni errores, y coincidieron con las etiquetas de referencia. Se registraron doce verdaderos positivos, cero falsos positivos y cero falsos negativos. Las catorce referencias devueltas resolvieron dentro de las fuentes. La latencia media fue 5964,98 milisegundos y el percentil 95, 8107,56 milisegundos, redondeados aquí a segundos. El evaluador empareja categoría o título y una línea admisible. Estos resultados no garantizan corrección semántica de todas las explicaciones ni generalización a otros repositorios. Esta evaluación corresponde al flujo directo, no a una evaluación amplia del planificador del agente. Esta corrida histórica se conserva como referencia de caecd71. No corresponde a 467d00e ni permite afirmar que v2 mejore al flujo directo. Christian coordina la comparación real final de los veinte casos; sus resultados están pendientes de incorporación.

Fuentes: docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37

## 9. Conocimiento curado y cobertura limitada

Tiempo: 60 segundos.

El inventario conserva ocho originales oficiales de MITRE y OWASP con URLs y hashes. El corpus ingerido comprende seis reglas curadas y no todas las páginas completas. La recuperación local del PR 37 recorrió veinte casos, de los cuales dieciocho tenían referencias esperadas. Para estos se obtuvo Recall@3 de 0,8056 y Precision@3 de 0,4630. Los dos casos fuera de cobertura no devolvieron fuentes. Estas métricas documentales usan un denominador distinto del recall de hallazgos. No se suman ni se intercambian. Su entorno es local, sin Gemini, y su latencia no representa Railway. Las condiciones no permiten atribuir una mejora causal frente a Semana 3.

Fuentes: docs/04-fuentes.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 10. Revisión del frontend integrado

Tiempo: 60 segundos.

Sobre la base integrada 467d00e se amplió la prueba de navegador para verificar datos visibles del presupuesto, aprobación, rechazo y caducidad tanto en ZIP como en GitHub. Se comprobaron también consentimiento inicial, idempotencia, cambios de entrada, manifiesto alterado y bloqueo visual al vencer. Pasaron doce comprobaciones, además de 133 pruebas frontend. Las veinticuatro HTTP omitidas no se cuentan como aprobadas. Lint terminó correctamente. La configuración temporal del fixture no cambia flags del proyecto ni producción. El agente conserva sus evidencias históricas; esta corrida no vuelve a evaluar Gemini real.

Fuentes: docs/evidencias/semana-4/cierre-agente-presupuesto-20261107/README.md

## 11. Documentación que permite revisar el producto

Tiempo: 70 segundos.

Se consolidó el documento del agente para explicar propósito, herramientas v2, bucle, límites, evidencia, confirmaciones, evaluación y riesgos. El documento 17 remite al principal y su versión anterior queda archivada. Se conservaron las doce historias existentes, incluidas las ocho solicitadas, con Dado, Cuando y Entonces. El inventario concuerda con ocho copias oficiales y seis reglas curadas. No se alteró el corpus ni se presentan estos documentos como evidencia original de Semana 1.

Fuentes: docs/08-agente.md; docs/02-requisitos.md; docs/04-fuentes.md; docs/evidencias/semana-4/cierre-agente-presupuesto-20261107/README.md

## 12. Comparación final pendiente

Tiempo: 50 segundos.

La comparación final todavía debe incorporarse. La plantilla de resultados identifica commit, modelo, corpus y dataset congelado. Mantendrá los denominadores, errores y estados parciales, y separará métricas documentales de detección. Se informarán precisión, recall, F1, latencia e intentos por ruta cuando estén respaldados por la evidencia. No se llenan ausencias con cero ni se atribuye una mejora al agente antes de observarla. La política de prioridad ya está integrada; la activación del presupuesto y el despliegue siguen bajo coordinación. La exposición tiene doce minutos planificados, no un ensayo acreditado.

Fuentes: docs/presentacion/comparacion-final-pendiente.md; eval/README.md
