# Guion de doce minutos: agente v2 y presupuesto

Referencia: `9c97ca1c8797bad5bdfdf227dba119b7839d32c7`. Duración planificada: 720 segundos, sin preguntas. No es un ensayo cronometrado. La comparación real final se incorporará después.

## 1. CODEGUARD

Tiempo: 30 segundos.

Presentamos CODEGUARD, revisión asistida de Python con herramientas estáticas, recuperación documental y agente supervisado. La referencia común de esta revisión es 9c97ca1, integrada por PR 45. Ronald revisa frontend y documentación. La exposición distingue el recorrido implementado, las pruebas controladas y la evaluación real histórica. La comparación final de veinte casos está a cargo de Christian y se incorporará después. El equipo debe confirmar el reparto de voces y ensayar los doce minutos.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45

## 2. Una revisión útil necesita evidencia

Tiempo: 60 segundos.

Explicar el problema con una consulta SQL construida por concatenación. El producto ayuda a localizar el patrón y a entender la recomendación. No afirmar que reemplaza una auditoría ni que cualquier alerta sea explotable. El valor esperado es facilitar revisión y trazabilidad; no tenemos una medición con usuarios que cuantifique tiempo ahorrado. Separar valor esperado de resultados medidos.

Fuentes: docs/01-propuesta.md

## 3. Del código al informe

Tiempo: 60 segundos.

La arquitectura integra entrada validada, Ruff/Bandit y AST, recuperación documental y síntesis. Para código pegado y .py el frontend solicita agente v2. Las decisiones pueden ampliar una ventana de código, buscar una referencia por categoría permitida o finalizar. El límite es tres pasos totales, dos decisiones y una síntesis, con hasta nueve intentos Gemini y plazo cooperativo de 150 segundos. ZIP y GitHub siguen el análisis directo por archivo. Su consentimiento de presupuesto es un recorrido separado y está apagado por defecto. La fusión de PR 45 no acredita la revisión que está activa en Railway.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45; docs/contrato-agente-v2/README.md

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

Este consentimiento autoriza analizar un proyecto, no descargar una corrección. La previsualización guarda contenidos y muestra el presupuesto antes de llamar a Gemini. GitHub sí se consulta para preparar los archivos. La casilla comienza desmarcada y aprobar vincula sesión, identificador y hash a la instantánea. Se admiten hasta cinco Python, doce mil caracteres combinados y ZIP de hasta cinco MB. Hay hasta tres intentos por archivo, máximo quince por proyecto y plazo cooperativo de hasta 150 segundos. Los valores efectivos los devuelve Backend. Rechazar o cambiar la entrada antes de aprobar no autoriza consumo. Después de aprobar, dejar de esperar solo interrumpe el navegador. El modo Demo es una simulación separada. No activar la función en producción durante la exposición.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45; docs/28-presupuesto-proyectos.md

## 7. El informe comunica sus límites

Tiempo: 60 segundos.

La priorización actual ordena por severidad y categoría, con empates estables. La interfaz preserva el orden y muestra bandas derivadas de severidad. Esto todavía no cumple la política severidad por confianza solicitada: Backend debe definir fórmula, criterios y procedencia de la confianza, además de probarla. No inventamos una confianza de Gemini a partir de la confianza de Bandit. El estado parcial sigue visible y las capas de hallazgos mantienen su procedencia. Un análisis incompleto no debe interpretarse como validación de seguridad.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45; docs/23-integracion-confirmacion-qa.md

## 8. Referencia histórica con Gemini real

Tiempo: 60 segundos.

El PR 37 conserva una corrida real del endpoint de análisis sobre veinte casos congelados. Completaron los veinte informes, sin respuestas parciales ni errores, y coincidieron con las etiquetas de referencia. Se registraron doce verdaderos positivos, cero falsos positivos y cero falsos negativos. Las catorce referencias devueltas resolvieron dentro de las fuentes. La latencia media fue 5964,98 milisegundos y el percentil 95, 8107,56 milisegundos, redondeados aquí a segundos. El evaluador empareja categoría o título y una línea admisible. Estos resultados no garantizan corrección semántica de todas las explicaciones ni generalización a otros repositorios. Esta evaluación corresponde al flujo directo, no a una evaluación amplia del planificador del agente. Esta corrida histórica se conserva como referencia de caecd71. No corresponde a 9c97ca1 ni permite afirmar que v2 mejore al flujo directo. Christian coordina la comparación real final de los veinte casos; sus resultados están pendientes de incorporación.

Fuentes: docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37

## 9. Conocimiento curado y cobertura limitada

Tiempo: 60 segundos.

El inventario conserva ocho originales oficiales de MITRE y OWASP con URLs y hashes. El corpus ingerido comprende seis reglas curadas y no todas las páginas completas. La recuperación local del PR 37 recorrió veinte casos, de los cuales dieciocho tenían referencias esperadas. Para estos se obtuvo Recall@3 de 0,8056 y Precision@3 de 0,4630. Los dos casos fuera de cobertura no devolvieron fuentes. Estas métricas documentales usan un denominador distinto del recall de hallazgos. No se suman ni se intercambian. Su entorno es local, sin Gemini, y su latencia no representa Railway. Las condiciones no permiten atribuir una mejora causal frente a Semana 3.

Fuentes: docs/04-fuentes.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 10. Revisión del frontend integrado

Tiempo: 60 segundos.

Ronald repitió los recorridos con los ejecutores locales existentes sobre la referencia 9c97ca1 y el ajuste del encabezado de error del presupuesto. Las 132 unitarias aprobaron; veinticuatro HTTP de la suite unitaria se omiten al no configurar su servidor. Los runners de navegador verifican seis escenarios del agente y nueve del presupuesto usando FastAPI, SQLite, recuperación local y analizadores reales. Gemini y GitHub externos están simulados. La caducidad ahora muestra Solicitud no completada, sin afirmar que falte integrar la aplicación. Las cifras previas de 495 pruebas backend y la suite HTTP del candidato corresponden a sus evidencias originales y no se presentan como corridas nuevas de Ronald. No se probó Railway ni se volvió a evaluar Gemini real.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45; docs/evidencias/semana-4/revision-ronald-v2-presupuesto-20261106/README.md

## 11. Documentación que permite revisar el producto

Tiempo: 70 segundos.

Mi aporte de frontend y documentación conecta lo que ve el usuario con los contratos y las pruebas. La matriz de trazabilidad identifica contexto y referencias, terminación y errores, exportación, consentimiento, caducidad y vista móvil. Se corrigen documentos que aún decían que la interfaz no soportaba v2. Las evidencias históricas conservan su versión y autoría. No se equipara una prueba controlada con Gemini simulado a una evaluación de calidad real. La presentación incorpora el recorrido nuevo y deja abierta la comparación final que coordina Christian.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45

## 12. Cierre coordinado sobre una misma versión

Tiempo: 50 segundos.

La referencia de revisión es 9c97ca1 y cualquier ajuste se entrega por rama y PR independiente. El presupuesto permanece desactivado por defecto. La integración del código no confirma por sí sola la versión desplegada. Backend completará la fórmula severidad por confianza y sus pruebas. Christian coordinará los veinte casos, verificará Railway y consolidará el paquete. Cuando entregue esos resultados se actualizarán las métricas y sus fuentes. Esta exposición no anticipa conclusiones de la evaluación final ni declara cerrados los requisitos académicos sin evidencia. Reservamos preguntas fuera de los doce minutos.

Fuentes: docs/29-revision-frontend-agente-presupuesto.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/45
