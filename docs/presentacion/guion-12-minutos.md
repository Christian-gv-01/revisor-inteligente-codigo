# Guion de sustentación actualizado con PR #37

Duración planificada: 720 segundos (12 minutos), sin preguntas. No es un ensayo cronometrado.
Versión evaluada: `caecd719a92fa40c060f24051b765e77721ee19b`. Evidencia del 6 de noviembre de 2026.

## 1. CODEGUARD

Tiempo: 30 segundos.

Presentamos CODEGUARD, un revisor asistido de código Python. Esta exposición recorre el problema, la arquitectura, la revisión humana y los resultados documentados. Ronald explica su aporte de frontend y documentación. La integración corresponde al PR 36, commit caecd71. Los resultados reales proceden del PR 37 y de la corrida del 6 de noviembre de 2026. No atribuir a Ronald la ejecución de las pruebas realizadas por Christian. El equipo debe confirmar el reparto final de expositores.

Fuentes: https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/36; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37

## 2. Una revisión útil necesita evidencia

Tiempo: 60 segundos.

Explicar el problema con una consulta SQL construida por concatenación. El producto ayuda a localizar el patrón y a entender la recomendación. No afirmar que reemplaza una auditoría ni que cualquier alerta sea explotable. El valor esperado es facilitar revisión y trazabilidad; no tenemos una medición con usuarios que cuantifique tiempo ahorrado. Separar valor esperado de resultados medidos.

Fuentes: docs/01-propuesta.md

## 3. Del código al informe

Tiempo: 60 segundos.

La entrada se valida antes del análisis. Ruff, Bandit y AST aportan evidencia estática, y RAG recupera documentos para la síntesis y sus citas. Código pegado y archivos .py usan el agente integrado. ZIP y GitHub conservan el flujo directo por archivo. FastAPI y React comparten dominio en Railway. El PR 36 integró frontend y backend en caecd71. El PR 37 verificó ese commit desplegado y la recuperación del índice. La disponibilidad de endpoints no implica que la opción de correcciones esté habilitada en la interfaz pública.

Fuentes: docs/03-arquitectura.md; docs/17-agente-integrado.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 4. Cada resultado conserva su origen

Tiempo: 70 segundos.

Mostrar que un mismo riesgo puede aparecer en más de una capa. Por eso no sumamos los contadores como si fueran vulnerabilidades distintas. La interfaz conserva la procedencia, las citas de cada archivo y el estado de cada herramienta. Una referencia de Bandit no se convierte en una cita OWASP por iniciativa del frontend. La traza muestra acciones observables; no es una supuesta transcripción del razonamiento privado del modelo.

Fuentes: frontend/src/components/FindingsPanel.tsx; frontend/src/components/AgentTracePanel.tsx; docs/10-analisis-estatico.md

## 5. La aprobación ocurre después de revisar

Tiempo: 70 segundos.

El contrato v1 ya está integrado. La previsualización permite comparar original y propuesta antes de tomar una decisión. La casilla comienza desmarcada y aprobar únicamente autoriza descargar la copia revisada. Sesión, identificador, hashes y caducidad vinculan la decisión a una propuesta concreta. El frontend verifica que la respuesta coincida con el contenido mostrado. Cancelar o cambiar la entrada invalida el consentimiento y descarta respuestas tardías. No se ejecuta el código ni se sobrescriben originales. El PR 37 registra además aprobación, idempotencia, rechazo y conflictos mediante HTTP con propuestas reales. La caducidad y el flujo visual corresponden a CI controlado con Gemini simulado.

Fuentes: docs/23-integracion-confirmacion-qa.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 6. Demostración del flujo de corrección

Tiempo: 70 segundos.

Esta demostración didáctica usa el ejemplo SQL fijo en modo Demo y no constituye una respuesta nueva de Gemini. En setenta segundos: analizar el ejemplo, abrir la propuesta y comparar ambos textos. Mostrar que no se puede descargar sin consentimiento. Cancelar, reabrir y comprobar que la casilla vuelve a estar desmarcada. Autorizar y descargar una copia con otro nombre, sin ejecutar el archivo. El mismo flujo cuenta por separado con siete escenarios de navegador contra FastAPI y SQLite reales, con Gemini simulado. Si no se dispone del entorno local durante la exposición, describir los pasos con las capturas de respaldo y conservar esa etiqueta de simulación.

Fuentes: frontend/src/services/correctionDemo.ts; docs/23-integracion-confirmacion-qa.md; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/36

## 7. El informe comunica sus límites

Tiempo: 60 segundos.

La priorización integrada ordena primero por severidad y después por categoría normalizada: seguridad, desconocida y calidad. Mantiene el orden estable en los empates. El frontend conserva ese orden y muestra bandas de revisión derivadas de severidad. Esta política no recalcula de forma independiente la severidad asignada por Gemini ni prueba explotabilidad. El estado parcial indica que el informe está incompleto aunque conserve resultados útiles. Las fuentes del informe y la traza del agente permiten revisar el origen de los datos. No deben sumarse alertas estáticas y generativas como si fueran riesgos necesariamente distintos.

Fuentes: docs/23-integracion-confirmacion-qa.md; backend/app/config/priorizacion.py; frontend/src/components/FindingsPanel.tsx

## 8. Resultados con Gemini real

Tiempo: 60 segundos.

El PR 37 conserva una corrida real del endpoint de análisis sobre veinte casos congelados. Completaron los veinte informes, sin respuestas parciales ni errores, y coincidieron con las etiquetas de referencia. Se registraron doce verdaderos positivos, cero falsos positivos y cero falsos negativos. Las catorce referencias devueltas resolvieron dentro de las fuentes. La latencia media fue 5964,98 milisegundos y el percentil 95, 8107,56 milisegundos, redondeados aquí a segundos. El evaluador empareja categoría o título y una línea admisible. Estos resultados no garantizan corrección semántica de todas las explicaciones ni generalización a otros repositorios. Esta evaluación corresponde al flujo directo, no a una evaluación amplia del planificador del agente.

Fuentes: docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37

## 9. Conocimiento curado y cobertura limitada

Tiempo: 60 segundos.

El inventario conserva ocho originales oficiales de MITRE y OWASP con URLs y hashes. El corpus ingerido comprende seis reglas curadas y no todas las páginas completas. La recuperación local del PR 37 recorrió veinte casos, de los cuales dieciocho tenían referencias esperadas. Para estos se obtuvo Recall@3 de 0,8056 y Precision@3 de 0,4630. Los dos casos fuera de cobertura no devolvieron fuentes. Estas métricas documentales usan un denominador distinto del recall de hallazgos. No se suman ni se intercambian. Su entorno es local, sin Gemini, y su latencia no representa Railway. Las condiciones no permiten atribuir una mejora causal frente a Semana 3.

Fuentes: docs/04-fuentes.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 10. Integración y verificación del despliegue

Tiempo: 60 segundos.

El PR 36 conserva 286 pruebas backend y diez QA, 296 en total. Las pruebas específicas ya están incluidas y no se suman otra vez. El frontend registra 91 unitarias, lint y build correctos. La integración HTTP con estático aprobó 24 de 24; sin estático, diecinueve y cinco no aplicables. El navegador registra siete casos con backend real y Gemini simulado, además de ocho escenarios demo separados. El PR 37 documenta seis workflows aprobados en main sobre caecd71, incluido Docker, y el commit activo en Railway. En ese despliegue aprobó la matriz pública de 26 escenarios y el smoke HTTP de nueve aserciones del agente y las correcciones. P26 solo evalúa AST local. La prueba real de correcciones es HTTP: no demuestra que el control visual esté habilitado públicamente.

Fuentes: https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/36; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/; https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/37

## 11. Documentación que permite revisar el producto

Tiempo: 70 segundos.

Mi aporte como Ronald es conectar el comportamiento visible con requisitos verificables y documentar el producto. Las ocho historias cubren previsualización, consentimiento, cancelación, invalidación, prioridad, estado parcial, citas y proceso del agente. La arquitectura y el inventario describen lo implementado. El PR 37 añade trazabilidad entre observaciones, cambios, pruebas y límites. La integración está completada y ya no debe describirse como futura. Las evidencias históricas se conservan con su fecha. La documentación distingue pruebas simuladas, backend real con proveedor simulado y pruebas HTTP con Gemini real. No se inventan entrevistas o actas faltantes.

Fuentes: docs/21-frontend-producto.md; docs/02-requisitos.md; docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/

## 12. Resultados y límites del producto

Tiempo: 50 segundos.

CODEGUARD integra interfaz, agente, análisis estático, recuperación documental y confirmación humana. La evidencia corresponde a una versión identificada y separa simulación de uso real de Gemini. La aplicación ayuda a revisar y no garantiza ausencia de vulnerabilidades. La aprobación de una copia tampoco garantiza la calidad semántica de la corrección. Quedan revisión semántica más amplia, evaluación del agente y aceptación del equipo. La activación del control de correcciones en la interfaz pública requiere una decisión independiente. La instalación limpia cronometrada y el levantamiento auténtico son pendientes académicos distintos. Cerrar en doce minutos y dejar las preguntas fuera de este tiempo.

Fuentes: docs/24-validacion-real-postmerge.md; docs/evidencias/semana-4/postmerge-caecd71-20261106/
