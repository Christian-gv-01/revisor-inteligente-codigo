
# 09. Decisiones arquitectónicas (ADR)

**Proyecto:** Revisor Inteligente de Código Seguro
**Estado:** Borrador pendiente de aprobación del equipo.
**Responsabilidad:** QA, seguridad y documentación técnica.

Este documento registra las decisiones arquitectónicas del proyecto.
Las propuestas aquí descritas deben contrastarse con el código
existente y aprobarse por el equipo antes de considerarse definitivas.

## ADR-001: Proveedor y modelo generativo

### Contexto
El sistema contempla el uso de inteligencia artificial generativa
para apoyar el análisis de código Python.

En la configuración de ejemplo del repositorio aparecen las
variables GEMINI_API_KEY y GEMINI_MODEL.

### Alternativas
- Utilizar Google Gemini.
- Utilizar otro proveedor de IA generativa.
- Utilizar un analizador estático sin un modelo generativo.

### Decisión propuesta
Evaluar Google Gemini como proveedor inicial, con el modelo
configurado mediante GEMINI_MODEL y la credencial almacenada
en GEMINI_API_KEY.

El proveedor y el modelo definitivos quedan pendientes de
confirmación por el equipo.

### Ventajas
- Permite configurar el modelo sin escribir su nombre directamente
  en la lógica de la aplicación.
- Facilita sustituir el modelo mediante configuración.
- Permite separar las credenciales del código fuente.

### Riesgos
- Límites de uso, errores y tiempos de espera del proveedor.
- Dependencia de un servicio externo.
- Posible exposición de código sensible si se envía sin controles.

### Responsable
Equipo de backend e integrante responsable de QA y seguridad.

### Estado
Propuesto; pendiente de aprobación.

## ADR-002: Uso de un workflow controlado

### Contexto
El sistema debe organizar el análisis de código de forma
predecible, controlada y verificable.

### Alternativas
- Ejecutar un flujo de análisis con etapas definidas.
- Delegar todas las decisiones a un agente autónomo.
- Combinar un flujo controlado con componentes inteligentes
  bajo límites definidos.

### Decisión propuesta
Priorizar un workflow controlado con etapas explícitas,
validaciones y manejo de errores.

La implementación completa del agente se considera pendiente
de acuerdo con el cronograma del proyecto.

### Ventajas
- Facilita reproducir y probar los resultados.
- Permite controlar entradas, errores y límites.
- Simplifica la auditoría del proceso.

### Riesgos
- Requiere definir las etapas y sus contratos.
- Los cambios en el flujo pueden exigir actualizar las pruebas.

### Responsable
Equipo de backend y responsable de arquitectura.

### Estado
Propuesto; pendiente de aprobación.


## ADR-003: Seguridad de claves y datos

### Contexto
El sistema puede manejar credenciales de proveedores y código
fuente que debe tratarse como información potencialmente sensible.

### Alternativas
- Guardar las credenciales directamente en el código.
- Utilizar variables de entorno y excluir los archivos locales
  con secretos del control de versiones.
- Utilizar un gestor de secretos cuando la infraestructura
  del proyecto lo permita.

### Decisión propuesta
No incluir credenciales en el código fuente ni en los commits.
Utilizar variables de entorno para la configuración local,
mantener los archivos con secretos fuera del repositorio y
evitar que las claves o el código sensible aparezcan en los logs.

La configuración de ejemplo debe mostrar los nombres de las
variables, nunca sus valores secretos.

### Ventajas
- Reduce el riesgo de publicar credenciales.
- Facilita separar configuración y código.
- Mejora la protección de la información sensible.

### Riesgos
- Una configuración incorrecta puede exponer secretos.
- Los registros de errores pueden revelar información si no
  se revisan y controlan.
- Las variables de entorno requieren una gestión adecuada
  en cada entorno de ejecución.

### Responsable
Todo el equipo; revisión específica por QA y seguridad.

### Estado
Propuesto; verificar los controles implementados y aprobar.

## ADR-004: Aislamiento del código recibido

### Contexto
El sistema recibe código Python que puede contener errores,
contenido malicioso o instrucciones dirigidas a manipular
al modelo de inteligencia artificial.

### Alternativas
- Ejecutar o importar el código recibido.
- Analizar el contenido como datos sin ejecutarlo.
- Ejecutar código en un entorno aislado y restringido, únicamente
  si una funcionalidad futura lo requiere y ha sido aprobada.

### Decisión propuesta
Para el MVP, tratar el código recibido como datos no confiables.
No ejecutarlo ni importarlo durante el análisis.

Los comentarios e instrucciones incluidos en el código deben
tratarse como contenido no confiable y nunca como instrucciones
que puedan modificar las reglas del sistema.

También deben definirse límites de tamaño, tiempos de espera
y controles para archivos ZIP, incluyendo rutas de extracción
inseguras.

### Ventajas
- Reduce el riesgo de ejecución de código malicioso.
- Evita conceder privilegios innecesarios al contenido recibido.
- Facilita diseñar pruebas de seguridad específicas.

### Riesgos
- El análisis de texto no elimina todos los riesgos.
- Los archivos comprimidos pueden contener rutas maliciosas
  o consumir recursos excesivos.
- El aislamiento completo requiere controles adicionales.

### Responsable
Equipo de backend y responsable de QA y seguridad.

### Estado
Propuesto; pendiente de aprobación y verificación técnica.


## Registro de aprobación

Antes de cerrar estos ADR, el equipo debe confirmar:

- El proveedor y el modelo generativo definitivos.
- El diseño del workflow controlado.
- Las medidas concretas de protección de secretos y datos.
- Los controles de aislamiento y validación de archivos.
