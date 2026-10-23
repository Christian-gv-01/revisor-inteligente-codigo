# Revisión de seguridad del sistema

**Proyecto:** Revisor Inteligente de Código Seguro\
**Responsable:** Área de QA y seguridad\
**Rama:** `feature/qa-seguridad`\
**Estado:** Revisión inicial en curso

## 1. Protección de credenciales

**Riesgo:** exposición de claves de API y otros secretos.

### Controles verificados

-   El archivo `.gitignore` excluye `.env` y `.env.*`.
-   La excepción `!.env.example` permite mantener un archivo de
    configuración de ejemplo.
-   `git check-ignore -v .env` confirmó que Git ignora `.env`.
-   `git ls-files -- .env` no devolvió resultados, por lo que `.env` no
    está registrado actualmente en el índice de Git.
-   El archivo `.env.example` contiene los nombres de las variables de
    configuración y no presenta valores de claves reales en el contenido
    revisado.
-   La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó
    con una clave ficticia incluida deliberadamente en un error
    simulado.
-   La prueba `test_servicio_no_registra_claves_ni_codigo_sensible` verifica que la clave ficticia y el código sensible no aparezcan en los registros capturados durante un error simulado del proveedor.

### Controles pendientes

-   Revisar el tratamiento de excepciones inesperadas.
-   Verificar que las credenciales no hayan sido publicadas previamente
    en el historial de Git.

**Estado:** protección local de `.env` verificada y prueba automatizada
de no exposición de una clave ficticia aprobada. La revisión completa de
credenciales y errores sigue pendiente.

## 2. Validación de archivos y entradas
**Riesgo:** recepción de entradas vacías, demasiado grandes o de tipos no permitidos.

### Controles identificados

- `backend/app/services/files.py` acepta archivos `.py` y valida el nombre.
- El límite de carga individual es de 1 MiB.
- Se exige UTF-8 y se rechazan archivos vacíos y bytes nulos.
- El código está limitado a 12.000 caracteres.
- Los límites excedidos producen HTTP 413 y las entradas inválidas HTTP 400.
- El archivo se lee en memoria, sin guardarlo ni ejecutarlo.

### Evidencia

- `backend/tests/test_uploads.py` contiene pruebas de carga válida, extensiones, rutas, codificación y límites.
- Las 23 pruebas específicas de carga pasaron en la ejecución registrada.

**Estado:** controles implementados y escenarios automatizados aprobados. Esto no sustituye una auditoría exhaustiva.

## 3. Seguridad de archivos ZIP
**Riesgo:** archivos comprimidos maliciosos, rutas inseguras y consumo excesivo de recursos.

### Controles identificados

- `backend/app/services/zip_files.py` limita el ZIP a 5 MiB.
- Se permiten hasta 100 entradas y 20 MiB de tamaño descomprimido declarado.
- Se admiten como máximo cinco archivos Python, de hasta 1 MiB cada uno.
- El código acumulado está limitado a 12.000 caracteres.
- Se rechazan rutas inseguras, nombres duplicados, entradas cifradas y tipos de archivo especiales.
- El contenido se procesa en memoria, sin extracción a disco ni ejecución del código.
- Se comprueba la codificación UTF-8 y se rechazan bytes nulos.

### Evidencia

- `backend/tests/test_uploads.py` comprueba ZIP válidos, corruptos, rutas inseguras, límites y contenido inválido, incluidos ZIP con más de 100 entradas y más de 20 MiB descomprimidos.
- Las 23 pruebas específicas de carga pasaron.

### Hallazgo pendiente

La implementación no captura explícitamente todas las posibles excepciones de descompresión, como `zlib.error` o `NotImplementedError`. Conviene coordinar pruebas adicionales con el responsable del backend.

**Estado:** controles principales implementados y pruebas existentes aprobadas. La gestión de todos los errores posibles de descompresión sigue pendiente de verificación.

## 4. Repositorios autorizados

**Riesgo:** acceso a repositorios no autorizados o a direcciones
internas.

### Resultado de la revisión inicial

-   Se buscaron referencias a GitHub, repositorios, solicitudes HTTP y
    validaciones de URL y direcciones IP en los archivos Python de
    `backend/app`.
-   La búsqueda no devolvió coincidencias.
-   No se ha confirmado una implementación de descarga o consulta de
    repositorios en los archivos examinados.

### Controles pendientes

-   Confirmar si la consulta de repositorios forma parte del alcance
    actual del MVP.
-   Restringir las solicitudes a repositorios públicos autorizados.
-   Validar el dominio, el esquema y la URL recibida.
-   Prevenir solicitudes hacia direcciones IP privadas, locales o
    internas.
-   Controlar redirecciones para evitar que conduzcan a destinos no
    autorizados.

**Estado:** no se identificaron referencias a esta funcionalidad en
`backend/app`. Los controles de acceso a repositorios están pendientes
de verificación.

## 5. Aislamiento del código recibido

**Riesgo:** ejecución accidental de código malicioso.

### Resultado de la revisión inicial

-   Se buscaron referencias a `exec()`, `eval()`, `compile()`,
    `__import__()`, `importlib`, `subprocess`, `runpy` y `os.system` en
    los archivos Python de `backend/app`.
-   La búsqueda no devolvió coincidencias.
-   El servicio `backend/app/services/llm.py` envía el código recibido
    al proveedor de IA como contenido para su análisis.
-   No se ha identificado una ejecución directa del código recibido en
    las partes examinadas.

### Controles pendientes

-   Revisar el flujo completo para descartar otras vías de ejecución.
-   Verificar que el código recibido nunca se ejecute ni se importe.
-   Comprobar el tratamiento de comentarios y cadenas que contengan
    instrucciones maliciosas.
-   Validar la salida generada por el modelo.

**Estado:** revisión estática inicial realizada. La verificación
completa del aislamiento sigue pendiente.

## 6. Límites de tiempo y recursos
**Riesgo:** consumo excesivo de recursos y errores por tiempos de espera del proveedor de IA.

### Controles y pruebas

- El backend limita las entradas y configura el tiempo de espera mediante `LLM_TIMEOUT_SECONDS`.
- `test_servicio_controla_timeout_504` pasó.
- `test_servicio_controla_timeout_real` pasó después de integrar la corrección del backend.
- La ejecución completa del 22 de octubre de 2026 registró 42 pruebas aprobadas y ninguna fallida.

**Estado:** el problema de timeout detectado anteriormente quedó corregido y verificado mediante la prueba específica y la suite completa.

**Pendiente:** verificar límites adicionales de recursos cuando se incorporen nuevas funcionalidades.

## 7. Protección de registros (logs)
**Riesgo:** exposición de código sensible o credenciales en registros y mensajes de error.

### Evidencia automatizada

- `test_endpoint_no_expone_clave_en_error_proveedor` pasó.
- `test_servicio_no_registra_claves_ni_codigo_sensible` pasó.
- Las pruebas verifican escenarios controlados de errores y protección de información sensible.

**Estado:** pruebas automatizadas aprobadas para los escenarios cubiertos. No se ha acreditado con esta evidencia una auditoría de todos los registros en un entorno de despliegue.

## 8. Instrucciones maliciosas dirigidas a la IA
**Riesgo:** comentarios o cadenas Python que intenten modificar las instrucciones del sistema, manipular el análisis o revelar información confidencial.

### Controles y evidencia

- El prompt V1 establece que el código recibido no debe ejecutarse.
- Los comentarios y las cadenas del código deben tratarse como datos, no como instrucciones.
- `test_servicio_trata_codigo_malicioso_como_datos` pasó en la suite automatizada.

**Limitación:** la prueba automatizada no demuestra por sí sola la resistencia del modelo generativo real frente a todos los intentos de manipulación.

**Pendiente:** recopilar y comparar los resultados reales de las tres versiones de prompts, incluidas las pruebas específicas de instrucciones maliciosas.

**Estado:** controles documentados y prueba automatizada aprobada; evaluación completa de las versiones de prompts pendiente.

## 9. Evidencias y seguimiento
### Resultados de pytest

- Prueba específica de timeout: aprobada.
- Pruebas específicas de carga Python y ZIP: 23 aprobadas.
- Suite completa ejecutada el 22 de octubre de 2026: 42 aprobadas, 0 fallidas.
- Duración de la suite completa: 1,94 segundos.
- Código de salida de pytest: 0.

### Evidencias

- `docs/evidencias/semana-2/pytest-resultados.txt`: salida de la última ejecución completa.
- `backend/tests/test_uploads.py`: pruebas automatizadas de carga de archivos.
- `docs/evidencias/semana-2/bitacora.md`: seguimiento de problemas y correcciones.

Los resultados anteriores de 15 aprobadas y 1 fallida, así como las ejecuciones parciales, son históricos. No deben presentarse como el resultado actual.

**Estado:** suite completa aprobada. La revisión de seguridad conserva los hallazgos adicionales que requieren verificación.

## 10. Observaciones
Esta revisión recoge los controles identificados en el código y los resultados de pruebas realmente ejecutadas.

### Conclusiones

- La carga de archivos Python y ZIP está implementada y cuenta con pruebas automatizadas aprobadas.
- La prueba de timeout que falló anteriormente pasó después de la corrección del backend.
- La suite completa registró 42 aprobadas y 0 fallidas.
- Las pruebas con mocks no acreditan por sí solas el comportamiento del proveedor de IA real.

### Pendientes de cierre

- Coordinar pruebas adicionales para errores de descompresión ZIP.
- Confirmar los controles de acceso a repositorios públicos autorizados cuando esa funcionalidad esté implementada.
- Recopilar evidencias de las tres versiones de prompts.
- Mantener documentados los controles que todavía no se han verificado.

No deben marcarse como aprobadas las protecciones que no cuentan con evidencia suficiente.
