
# 09. Decisiones arquitect├│nicas (ADR)

**Proyecto:** Revisor Inteligente de C├│digo Seguro
**Estado:** Borrador pendiente de aprobaci├│n del equipo.
**Responsabilidad:** QA, seguridad y documentaci├│n t├®cnica.

Este documento registra las decisiones arquitect├│nicas del proyecto.
Las propuestas aqu├¡ descritas deben contrastarse con el c├│digo
existente y aprobarse por el equipo antes de considerarse definitivas.

## ADR-001: Proveedor y modelo generativo

### Contexto
El sistema contempla el uso de inteligencia artificial generativa
para apoyar el an├ílisis de c├│digo Python.

En la configuraci├│n de ejemplo del repositorio aparecen las
variables GEMINI_API_KEY y GEMINI_MODEL.

### Alternativas
- Utilizar Google Gemini.
- Utilizar otro proveedor de IA generativa.
- Utilizar un analizador est├ítico sin un modelo generativo.

### Decisi├│n propuesta
Evaluar Google Gemini como proveedor inicial, con el modelo
configurado mediante GEMINI_MODEL y la credencial almacenada
en GEMINI_API_KEY.

El proveedor y el modelo definitivos quedan pendientes de
confirmaci├│n por el equipo.

### Ventajas
- Permite configurar el modelo sin escribir su nombre directamente
  en la l├│gica de la aplicaci├│n.
- Facilita sustituir el modelo mediante configuraci├│n.
- Permite separar las credenciales del c├│digo fuente.

### Riesgos
- L├¡mites de uso, errores y tiempos de espera del proveedor.
- Dependencia de un servicio externo.
- Posible exposici├│n de c├│digo sensible si se env├¡a sin controles.

### Responsable
Equipo de backend e integrante responsable de QA y seguridad.

### Estado
Propuesto; pendiente de aprobaci├│n.

## ADR-002: Uso de un workflow controlado

### Contexto
El sistema debe organizar el an├ílisis de c├│digo de forma
predecible, controlada y verificable.

### Alternativas
- Ejecutar un flujo de an├ílisis con etapas definidas.
- Delegar todas las decisiones a un agente aut├│nomo.
- Combinar un flujo controlado con componentes inteligentes
  bajo l├¡mites definidos.

### Decisi├│n propuesta
Priorizar un workflow controlado con etapas expl├¡citas,
validaciones y manejo de errores.

La implementaci├│n completa del agente se considera pendiente
de acuerdo con el cronograma del proyecto.

### Ventajas
- Facilita reproducir y probar los resultados.
- Permite controlar entradas, errores y l├¡mites.
- Simplifica la auditor├¡a del proceso.

### Riesgos
- Requiere definir las etapas y sus contratos.
- Los cambios en el flujo pueden exigir actualizar las pruebas.

### Responsable
Equipo de backend y responsable de arquitectura.

### Estado
Propuesto; pendiente de aprobaci├│n.


## ADR-003: Seguridad de claves y datos

### Contexto
El sistema puede manejar credenciales de proveedores y c├│digo
fuente que debe tratarse como informaci├│n potencialmente sensible.

### Alternativas
- Guardar las credenciales directamente en el c├│digo.
- Utilizar variables de entorno y excluir los archivos locales
  con secretos del control de versiones.
- Utilizar un gestor de secretos cuando la infraestructura
  del proyecto lo permita.

### Decisi├│n propuesta
No incluir credenciales en el c├│digo fuente ni en los commits.
Utilizar variables de entorno para la configuraci├│n local,
mantener los archivos con secretos fuera del repositorio y
evitar que las claves o el c├│digo sensible aparezcan en los logs.

La configuraci├│n de ejemplo debe mostrar los nombres de las
variables, nunca sus valores secretos.

### Ventajas
- Reduce el riesgo de publicar credenciales.
- Facilita separar configuraci├│n y c├│digo.
- Mejora la protecci├│n de la informaci├│n sensible.

### Riesgos
- Una configuraci├│n incorrecta puede exponer secretos.
- Los registros de errores pueden revelar informaci├│n si no
  se revisan y controlan.
- Las variables de entorno requieren una gesti├│n adecuada
  en cada entorno de ejecuci├│n.

### Responsable
Todo el equipo; revisi├│n espec├¡fica por QA y seguridad.

### Estado
Propuesto; verificar los controles implementados y aprobar.

## ADR-004: Aislamiento del c├│digo recibido

### Contexto
El sistema recibe c├│digo Python que puede contener errores,
contenido malicioso o instrucciones dirigidas a manipular
al modelo de inteligencia artificial.

### Alternativas
- Ejecutar o importar el c├│digo recibido.
- Analizar el contenido como datos sin ejecutarlo.
- Ejecutar c├│digo en un entorno aislado y restringido, ├║nicamente
  si una funcionalidad futura lo requiere y ha sido aprobada.

### Decisi├│n propuesta
Para el MVP, tratar el c├│digo recibido como datos no confiables.
No ejecutarlo ni importarlo durante el an├ílisis.

Los comentarios e instrucciones incluidos en el c├│digo deben
tratarse como contenido no confiable y nunca como instrucciones
que puedan modificar las reglas del sistema.

Tambi├®n deben definirse l├¡mites de tama├▒o, tiempos de espera
y controles para archivos ZIP, incluyendo rutas de extracci├│n
inseguras.

### Ventajas
- Reduce el riesgo de ejecuci├│n de c├│digo malicioso.
- Evita conceder privilegios innecesarios al contenido recibido.
- Facilita dise├▒ar pruebas de seguridad espec├¡ficas.

### Riesgos
- El an├ílisis de texto no elimina todos los riesgos.
- Los archivos comprimidos pueden contener rutas maliciosas
  o consumir recursos excesivos.
- El aislamiento completo requiere controles adicionales.

### Responsable
Equipo de backend y responsable de QA y seguridad.

### Estado
Propuesto; pendiente de aprobaci├│n y verificaci├│n t├®cnica.


## Registro de aprobaci├│n

Antes de cerrar estos ADR, el equipo debe confirmar:

- El proveedor y el modelo generativo definitivos.
- El dise├▒o del workflow controlado.
- Las medidas concretas de protecci├│n de secretos y datos.
- Los controles de aislamiento y validaci├│n de archivos.
