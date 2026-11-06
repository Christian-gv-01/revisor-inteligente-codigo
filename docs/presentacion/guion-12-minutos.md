# Guion y notas — borrador de 12 minutos

Fecha: 6 de noviembre de 2026. Tiempos de ensayo propuestos, no medidos. El contrato de aprobación real sigue pendiente de acuerdo con Christian.

## 1. CODEGUARD

Tiempo: 30 segundos.

Presentación de doce minutos. Presentar el proyecto y al equipo: Ronald Yépez, Andy y Christian Gamboa. Aclarar que este archivo es un borrador para revisión conjunta. Ronald asume en esta asignación Frontend y documentación del producto. No asignar a Andy una nueva responsabilidad que todavía no se haya confirmado.

Fuentes: docs/01-propuesta.md; docs/21-frontend-producto.md

## 2. Una revisión útil necesita evidencia

Tiempo: 60 segundos.

Explicar el problema con una consulta SQL construida por concatenación. El producto ayuda a localizar el patrón y a entender la recomendación. No afirmar que reemplaza una auditoría ni que cualquier alerta sea explotable. El valor esperado es facilitar revisión y trazabilidad; no tenemos una medición con usuarios que cuantifique tiempo ahorrado. Separar valor esperado de resultados medidos.

Fuentes: docs/01-propuesta.md

## 3. Del código al informe

Tiempo: 60 segundos.

Recorrer las capas: entrada validada, herramientas, recuperación documental, síntesis y presentación. Código pegado y .py utilizan el agente integrado en la base revisada. ZIP y GitHub conservan análisis directo por archivo. El frontend y la API se sirven desde el mismo dominio en producción. Gemini es externo, ChromaDB contiene el índice curado y Ruff/Bandit analizan sin ejecutar el programa. La modificación actual es local; no se afirma que esté desplegada.

Fuentes: docs/03-arquitectura.md; docs/17-agente-integrado.md

## 4. Cada resultado conserva su origen

Tiempo: 70 segundos.

Mostrar que un mismo riesgo puede aparecer en más de una capa. Por eso no sumamos los contadores como si fueran vulnerabilidades distintas. La interfaz conserva la procedencia, las citas de cada archivo y el estado de cada herramienta. Una referencia de Bandit no se convierte en una cita OWASP por iniciativa del frontend. La traza muestra acciones observables; no es una supuesta transcripción del razonamiento privado del modelo.

Fuentes: frontend/src/components/FindingsPanel.tsx; frontend/src/components/AgentTracePanel.tsx; docs/10-analisis-estatico.md

## 5. La aprobación ocurre después de revisar

Tiempo: 70 segundos.

Explicar la diferencia entre preparar una propuesta como texto y generar el archivo descargable. La casilla empieza desmarcada y el botón de confirmación es independiente. La aplicación no ejecuta código ni escribe sobre el archivo original. El contenido descargado tiene que coincidir con el previsualizado. Si el usuario cancela, cambia de entrada o llega una respuesta anterior, no se utiliza esa aprobación. Mostrar explícitamente que la demostración es local y no una respuesta real de Gemini.

Fuentes: docs/20-contrato-confirmacion-humana.md; frontend/src/components/CorrectionPreview.tsx

## 6. Demostración del flujo de corrección

Tiempo: 70 segundos.

Reservar setenta segundos para interactuar. Analizar el ejemplo SQL inicial, seleccionar el hallazgo y abrir la propuesta. Mostrar el original junto a la consulta parametrizada. Antes de marcar la casilla, el botón de descarga debe estar deshabilitado. Cancelar y verificar que no se descargó nada. Reabrir: el consentimiento no debe conservarse. Marcar la casilla y confirmar. Mostrar el nombre usuarios.corregido.py y explicar que no se ejecuta el archivo. Si falla la demo, utilizar las capturas locales identificadas como simuladas.

Fuentes: frontend/src/services/correctionDemo.ts; docs/evidencias/semana-4/frontend-producto-20261106/

## 7. El informe comunica sus límites

Tiempo: 60 segundos.

La prioridad visible de esta rama es un orden de revisión derivado de la severidad actual: crítica, alta, media y baja. No representa una nueva estimación de impacto de negocio. Christian comunicó priorización determinista en su rama; antes de integrar se debe alinear su contrato y evitar duplicar reglas. La señal parcial aparece incluso cuando algunos hallazgos son válidos o el backend no incluye mensaje. Un resultado parcial no debe interpretarse como aprobación de seguridad.

Fuentes: frontend/src/components/FindingsPanel.tsx; frontend/src/components/StaticFindingsPanel.tsx

## 8. Qué prueban los resultados disponibles

Tiempo: 60 segundos.

Mantener las fechas y entornos separados. Las 91 pruebas son de esta edición frontend antes de la integración real de correcciones. Los 26 escenarios públicos pertenecen a la evidencia previa del 5 de noviembre. No sumarlos ni usarlos para acreditar el contrato nuevo en Railway. Mostrar cancelación, consentimiento y verificación del contenido como propiedades verificadas localmente. La compilación mantiene una advertencia conocida de tamaño del paquete. Actualizar esta diapositiva si cambia la validación final.

Fuentes: docs/21-frontend-producto.md; docs/evidencias/semana-4/produccion-integrada-20261105/pruebas-publicas.json

## 9. Conocimiento curado y cobertura limitada

Tiempo: 60 segundos.

Distinguir documentos originales descargados de resúmenes realmente ingeridos. El inventario conserva URLs, fechas y hashes; ChromaDB no contiene automáticamente cada página completa. Las reglas cubren ejecución dinámica, SQL, comandos, inyección general, secretos y rutas. Este corpus no respalda todos los patrones que detecta Bandit. Las métricas históricas de recuperación no prueban por sí mismas precisión de hallazgos generativos.

Fuentes: docs/04-fuentes.md; data/raw/fuentes.json; knowledge/seguridad_python.md

## 10. Un cambio local no altera producción

Tiempo: 60 segundos.

Explicar la advertencia del equipo: Railway puede estar conectado a main mediante configuración externa. Los workflows revisados no contienen despliegue, pero eso no certifica la configuración de la plataforma. Se conserva la rama solo localmente, sin cambiar backend, Docker o variables de Railway. Antes de cualquier publicación hay que revisar la política real de despliegue con Christian. No prometer que cualquier rama remota sea inocua por el solo hecho de no llamarse main.

Fuentes: docs/21-frontend-producto.md; .github/workflows/

## 11. Documentación que permite revisar el producto

Tiempo: 70 segundos.

Ronald explica su responsabilidad actual de Frontend y documentación del producto. La documentación previa de QA se conserva con su autoría y fecha; cambiar de rol no reescribe la historia. Las ocho historias específicas cubren previsualización, consentimiento, cancelación, invalidación de propuesta, prioridad, estado parcial, citas y traza. Los documentos distinguen implementación local, contrato propuesto e integración pendiente. No se inventaron entrevistas ni actas para cubrir requisitos históricos.

Fuentes: docs/21-frontend-producto.md; docs/02-requisitos.md; docs/11-aportes-ia.md

## 12. El siguiente cierre es la integración acordada

Tiempo: 50 segundos.

Cerrar recordando el alcance: la interfaz local y los documentos están preparados, pero no se afirma integración real de endpoints que aún no existen. Confirmar los campos con Christian, probarlos sobre backend local o entorno candidato autorizado y luego coordinar publicación. La aplicación ayuda a revisar, no garantiza ausencia de vulnerabilidades. Reservar la última frase para una demostración de la copia aprobada o para abrir las preguntas del jurado.

Fuentes: docs/20-contrato-confirmacion-humana.md; docs/21-frontend-producto.md

