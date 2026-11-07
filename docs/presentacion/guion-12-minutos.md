# Guion acordado: diez diapositivas, doce minutos planificados

Fuente: reparto comunicado por Christian el 7 de noviembre de 2026. Integrantes:
Christian Gamboa, Ronald Yépez y Klever Andres Alban Cruz (Andy).
La ejecución técnica y el guion no sustituyen el registro cronometrado.

## 1. Christian: problema y público (0:00-1:00, diapositiva 1)

Presentar al equipo y el problema: desarrolladores y revisores de Python necesitan
localizar riesgos y comprobar su evidencia. CODEGUARD combina herramientas estáticas,
RAG y un agente supervisado. El código recibido se trata como texto, sin ejecutarlo.

## 2. Christian: demostración (1:00-5:00, diapositivas 2-4)

1:00-3:00: seleccionar API real y **Agente**; la ruta inicial ahora es Directa.
Cargar caso_01.py. Mostrar hallazgo, ubicación, fuente y proceso del agente. Separar
observaciones Ruff/Bandit de hallazgos Gemini + RAG; no sumarlos como riesgos distintos.
3:00-4:00: mostrar abstención real cuando falte respaldo. El ejemplo P19 de la
evaluación histórica fue abstenido por ambas rutas, pero no se promete una salida
idéntica en cada llamada nueva. La ausencia de evidencia no certifica seguridad.
4:00-5:00: previsualizar, comparar original/propuesta y señalar cancelar. Autorizar
solo si se acepta el contenido revisado; descargar copia sin ejecutarla ni sobrescribir
el original. Previsualizar puede consumir Gemini antes de aprobar la descarga.
Si el proveedor falla, conservar y explicar el parcial; anunciar cualquier modo Demo
como simulación y distinguirlo de la evidencia histórica real.

## 3. Ronald: arquitectura y agente (5:00-7:00, diapositivas 5-6)

React, TypeScript y Monaco constituyen la interfaz; FastAPI valida solicitudes.
Ruff/Bandit y AST inspeccionan, ChromaDB recupera fuentes y Gemini sintetiza.
Código y .py ofrecen **Directa predeterminada y Agente opcional**. ZIP/GitHub
conservan la ruta directa por archivo. El usuario elige Agente para explorar decisiones
trazables, aceptando más llamadas/tiempo potenciales. Máximo cuatro pasos; el revisor
principal solicita tres al optar por Agente. Las herramientas son limitadas y sus
resultados participan en la decisión siguiente. No hay ejecución libre del código.

## 4. Klever: pruebas, pipeline y evaluación (7:00-9:00, diapositivas 7-8)

Mostrar la revisión asociada a las evidencias; separar proveedores simulados de Gemini
real. Las cifras 589 backend + 80 QA/evaluadores y 146 frontend corresponden al cierre
anterior identificado, no a una suite nueva inventada por cambiar el guion.
En la corrida c522c24: directa 17/20 informes completos y agente 14/20. F1 1,0 solo
en los trece pares comunes completos. No se demostró mayor precisión del agente.
Se conserva la corrida previa y los parciales; el contexto influyó en dos de cinco
pares comparables del A/B, lo que no mide calidad de informes.
Transición: «Estos resultados muestran tanto el funcionamiento como sus límites.
Ronald resumirá las medidas de seguridad».

## 5. Ronald: seguridad (9:00-10:00, diapositiva 9)

Código inspeccionado sin ejecución, validación de archivos, límites de entrada y
claves solo en backend. Dos permisos distintos: presupuesto autoriza analizar la
instantánea del proyecto; corrección autoriza descargar la copia revisada. Sesiones,
hashes y caducidad vinculan cada decisión al contenido. Rechazar presupuesto no añade
llamadas generativas; detener la espera no revoca llamadas ya iniciadas.

## 6. Klever: limitaciones y cierre (10:00-12:00, diapositiva 10)

Corpus pequeño, fallos del proveedor, posibles falsos positivos y negativos. Proponer
ampliar fuentes/casos, repetir comparaciones controladas y mejorar consumo/resiliencia.
Cerrar con trazabilidad y control humano, sin prometer una mejora de precisión que
no se demostró. La ruta directa inicial responde a la evidencia observada, sin convertir
una sola corrida exploratoria en garantía universal. Fuentes: docs/18, docs/37 y ADR E4-13.
