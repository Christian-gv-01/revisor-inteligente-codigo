# 09. Decisiones arquitectónicas (ADR)

**Proyecto:** Revisor Inteligente de Código Seguro

**Rama de trabajo:** `integration/revision-2`

**Fecha de revisión:** 23 de octubre de 2026


**Estado:** En revisión final del equipo para aceptación de ADR.

Este documento registra las decisiones arquitectónicas del proyecto, su estado de implementación y las verificaciones realizadas durante la revisión de QA.

Una decisión propuesta no se considera aprobada únicamente porque exista código relacionado. La aprobación definitiva corresponde al equipo responsable del proyecto.

## ADR-001: Proveedor y modelo generativo

### Contexto

El sistema utiliza inteligencia artificial generativa para analizar fragmentos de código Python e identificar posibles problemas de seguridad y calidad.

El backend incluye la integración con Google Gemini mediante la biblioteca `google-genai`.

La configuración utiliza las variables `GEMINI_API_KEY` y `GEMINI_MODEL`.

### Alternativas

- Utilizar Google Gemini como proveedor inicial.
- Utilizar otro proveedor de inteligencia artificial generativa.
- Utilizar analizadores estáticos como complemento del análisis mediante IA.

### Decisión propuesta

Utilizar Google Gemini como proveedor generativo inicial del MVP.

La implementación actual obtiene la clave desde `GEMINI_API_KEY` y el modelo desde `GEMINI_MODEL`. Cuando esta última variable no está definida, el servicio utiliza el valor predeterminado configurado en `backend/app/services/llm.py`.

La aprobación definitiva del proveedor y del modelo corresponde al equipo.

La configuración de ejemplo contiene variables relacionadas con Groq, pero no se ha confirmado que exista una integración funcional con ese proveedor en el servicio examinado.

### Ventajas

- Permite utilizar inteligencia artificial generativa para apoyar el análisis.
- Separa las credenciales del código fuente.
- Facilita configurar el modelo mediante variables de entorno.
- Permite validar estructuralmente las respuestas generadas.

### Riesgos

- Dependencia de un proveedor externo.
- Límites de uso y posibles errores de disponibilidad.
- Costes asociados al consumo de la API.
- Posible exposición de código sensible si no se aplican controles adecuados.
- Respuestas incorrectas o hallazgos inventados por el modelo.

### Responsable

Equipo de backend y responsable de QA y seguridad.

### Estado

**Implementación:** integración con Gemini identificada en el código.

**Pendiente:** aprobación definitiva del proveedor y del modelo, y confirmación de los requisitos de disponibilidad y costes.

## ADR-002: Uso de un workflow controlado

### Contexto

El sistema necesita organizar el análisis de código mediante etapas explícitas, validaciones y tratamiento de errores.

Un flujo controlado facilita reproducir las pruebas, revisar los resultados y verificar el comportamiento de cada componente.

### Alternativas

- Ejecutar un flujo de análisis con etapas definidas.
- Delegar todas las decisiones a un agente autónomo.
- Combinar un flujo controlado con componentes inteligentes sujetos a límites definidos.

### Decisión propuesta

Priorizar un workflow controlado en el que las solicitudes pasen por validaciones y etapas identificables.

La implementación actual incluye:

- Recepción de solicitudes mediante FastAPI.
- Validación de los datos con modelos Pydantic.
- Delegación del análisis al servicio de IA.
- Validación de la estructura de la respuesta.
- Gestión de determinados errores del proveedor.
- Devolución de resultados mediante una respuesta estructurada.

La implementación de un agente completo y de cualquier funcionalidad adicional de automatización debe confirmarse con el equipo.

### Ventajas

- Facilita las pruebas automatizadas.
- Permite identificar errores en etapas concretas.
- Reduce la dependencia de decisiones autónomas difíciles de verificar.
- Facilita documentar y auditar el flujo de análisis.

### Riesgos

- Requiere definir contratos claros entre componentes.
- Los cambios en el flujo pueden exigir actualizar las pruebas.
- Un manejo incompleto de excepciones puede interrumpir solicitudes.
- Las funcionalidades adicionales pueden introducir nuevos riesgos de seguridad.

### Responsable

Equipo de backend y responsable de arquitectura.

### Estado

**Implementación:** flujo básico de análisis controlado identificado en el backend.

**Pendiente:** confirmar el diseño definitivo, el alcance del agente y las etapas adicionales previstas.

## ADR-003: Seguridad de claves y datos

### Contexto

El sistema maneja credenciales de proveedores externos y recibe código fuente que puede contener información sensible.

La exposición accidental de secretos en el repositorio, los registros o las respuestas HTTP puede comprometer el sistema y los datos de sus usuarios.

### Alternativas

- Almacenar las credenciales directamente en el código.
- Utilizar variables de entorno y excluir los archivos locales con secretos del control de versiones.
- Incorporar un gestor de secretos cuando la infraestructura lo permita.

### Decisión propuesta

No incluir credenciales reales en el código fuente ni en los commits.

Utilizar variables de entorno para las credenciales, mantener los archivos locales con secretos fuera del repositorio y evitar que las claves o el código sensible aparezcan en los registros y las respuestas de error.

La configuración de ejemplo debe mostrar los nombres de las variables, nunca sus valores secretos.

### Controles verificados

- `.gitignore` excluye `.env` y `.env.*`, con una excepción para `.env.example`.
- `git check-ignore -v .env` confirmó que Git ignora `.env`.
- `git ls-files -- .env` no devolvió resultados.
- El contenido revisado de `.env.example` no presenta claves reales.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó con una clave ficticia incluida en un error simulado.

### Controles pendientes

- Verificar mediante pruebas específicas que los registros no expongan credenciales ni código sensible.
- Revisar el tratamiento de excepciones inesperadas.
- Confirmar que no existan credenciales expuestas en el historial de Git.
- Completar la revisión de los componentes que gestionen información sensible.

### Ventajas

- Reduce el riesgo de publicar credenciales.
- Facilita separar la configuración del código.
- Mejora la protección de información sensible.
- Permite comprobar el comportamiento de los errores mediante pruebas automatizadas.

### Riesgos

- Una configuración incorrecta puede exponer secretos.
- Los mensajes de error pueden divulgar información interna.
- Los registros pueden contener información sensible si no se controlan.
- Las variables de entorno requieren una gestión adecuada en cada entorno.

### Responsable

Todo el equipo, con revisión específica por QA y seguridad.

### Estado

**Implementación:** protección local de `.env` verificada y prueba automatizada de no exposición de una clave ficticia aprobada.

**Pendiente:** revisión completa de logs, excepciones inesperadas e historial de credenciales.

## ADR-004: Aislamiento del código recibido

### Contexto

El sistema recibe código Python que puede contener errores, instrucciones maliciosas o contenido destinado a manipular el comportamiento del modelo generativo.

El código debe analizarse como contenido no confiable y no ejecutarse durante la revisión.

### Alternativas

- Ejecutar o importar el código recibido.
- Analizar el contenido como datos sin ejecutarlo.
- Incorporar ejecución en un entorno aislado únicamente si una funcionalidad futura lo requiere y cuenta con aprobación y controles específicos.

### Decisión propuesta

Para el MVP, tratar el código recibido como datos no confiables y no ejecutarlo ni importarlo durante el análisis.

Los comentarios y las cadenas del código deben tratarse como contenido, no como instrucciones capaces de modificar las reglas del sistema.

También deben definirse límites de entrada y tiempo de espera. Cualquier funcionalidad futura de carga o extracción de ZIP deberá incorporar controles específicos para rutas inseguras y consumo excesivo de recursos.

### Controles identificados

- El prompt `backend/app/prompts/system_v1.md` establece que el código recibido nunca debe ejecutarse.
- El prompt indica que los comentarios y las cadenas deben tratarse como datos, nunca como instrucciones.
- El servicio envía el código al proveedor como contenido destinado al análisis.
- La respuesta generada se valida mediante el modelo `InformeModelo`.
- Se comprobaron las referencias a `exec()`, `eval()`, `compile()`, `__import__()`, `importlib`, `subprocess`, `runpy` y `os.system` en los archivos Python examinados de `backend/app`, sin encontrar coincidencias.

Estas comprobaciones estáticas no demuestran por sí solas que no existan todas las posibles vías de ejecución o vulnerabilidades.

### Controles pendientes

- Incorporar pruebas específicas frente a instrucciones maliciosas en comentarios y cadenas.
- Comprobar que las instrucciones del sistema se mantengan durante el análisis.
- Evaluar las respuestas manipuladas o inválidas del proveedor.
- Revisar el flujo completo ante posibles vías de ejecución indirecta.
- Confirmar si la carga y el procesamiento de archivos ZIP forman parte del alcance del MVP.
- Implementar controles de extracción segura si se incorpora esa funcionalidad.

### Ventajas

- Reduce el riesgo de ejecución accidental de código malicioso.
- Evita conceder privilegios innecesarios al contenido recibido.
- Facilita definir pruebas específicas de seguridad.
- Permite mantener una separación clara entre las instrucciones del sistema y los datos analizados.

### Riesgos

- El análisis mediante IA puede producir falsos positivos o falsos negativos.
- Las instrucciones maliciosas pueden intentar manipular el resultado.
- La validación estructural no garantiza que todos los hallazgos sean correctos.
- La incorporación de carga de archivos o ejecución de código requeriría controles adicionales.

### Responsable

Equipo de backend y responsable de QA y seguridad.

### Estado

**Implementación:** medidas de aislamiento identificadas en el prompt y en el servicio examinado.

**Pendiente:** pruebas específicas de seguridad y confirmación completa del aislamiento técnico.

## Registro de aprobación

Antes de cerrar estos ADR, el equipo debe confirmar:

- [ ] Proveedor y modelo generativo definitivos.
- [ ] Diseño del workflow controlado y alcance del agente.
- [ ] Medidas de protección de credenciales y datos.
- [ ] Política de registros y tratamiento de errores.
- [ ] Controles de aislamiento del código y resistencia ante instrucciones maliciosas.
- [ ] Alcance de la carga de archivos y del procesamiento de ZIP.

La aprobación definitiva debe registrarse cuando el equipo haya revisado las decisiones y confirmado su correspondencia con la implementación y los requisitos del proyecto.


## Actualización técnica — Revisión 2

**Fecha:** 23 de octubre de 2026  
**Referencia:** Rama `integration/revision-2`

### ADR-001 — Proveedor generativo

Se ha comprobado la integración real con Google Gemini mediante FastAPI.

El modelo utilizado en las pruebas de comparación es `gemini-3.5-flash-lite`, configurado mediante la variable de entorno `GEMINI_MODEL`.

El backend incorpora validación de las respuestas mediante Pydantic y manejo controlado de determinados errores del proveedor.

**Limitación:** no se ha implementado todavía un proveedor de respaldo operativo ni un sistema completo de reintentos.

**Estado propuesto:** Aceptado para el MVP, sujeto a confirmación del equipo.

### ADR-002 — Workflow controlado

Se ha implementado una secuencia explícita de recepción, validación, llamada al modelo y devolución de un informe JSON estructurado.

Se dispone de endpoints para fragmentos Python, archivos `.py` y archivos ZIP.

**Decisión:** mantener un workflow controlado durante la segunda semana. La integración de herramientas Ruff, Bandit, RAG y el agente corresponde a fases posteriores.

**Estado propuesto:** Aceptado para el MVP, sujeto a confirmación del equipo.

### ADR-003 — Protección de secretos

Las credenciales se cargan desde variables de entorno en el backend. El archivo `.env` está excluido del control de versiones y la configuración de ejemplo no debe contener credenciales reales.

Se han ejecutado pruebas automatizadas de manejo de errores y de protección de información sensible.

**Limitación:** la revisión del historial Git y de posibles secretos históricos debe documentarse de forma independiente.

**Estado propuesto:** Aceptado para el MVP, sujeto a confirmación del equipo.

### ADR-004 — Procesamiento de código no confiable

El sistema analiza código Python como contenido textual, sin ejecutar ni importar el código enviado por el usuario.

La carga de `.py` y ZIP incluye controles de tamaño, formato, rutas y contenido.

Se implementó manejo de excepciones de descompresión, incluida `zlib.error`.

**Limitación:** los controles actuales no constituyen un aislamiento completo del proceso. Falta validar exhaustivamente la resistencia a inyección de prompt y archivos maliciosos.

**Estado propuesto:** Aceptado para el MVP, sujeto a confirmación del equipo.

### Evidencia disponible

- Integración real React → FastAPI → Gemini.
- 40 pruebas de backend aprobadas antes de incorporar las nuevas pruebas de regresión ZIP.
- 38 pruebas de frontend aprobadas.
- Comparación experimental inicial de los tres prompts en `docs/05-prompts.md`.
- Capturas y resultados almacenados en `docs/evidencias/semana-2/`.

### Aprobación grupal

**Tech Lead / Backend:** Pendiente de registrar confirmación.  
**Frontend:** Pendiente de registrar confirmación.  
**QA / Seguridad:** Pendiente de registrar confirmación.

El equipo deberá registrar la aceptación definitiva y los responsables mediante un commit de documentación.

