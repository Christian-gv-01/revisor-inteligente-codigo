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

### Controles pendientes

-   Comprobar mediante pruebas específicas que los registros no revelen
    credenciales.
-   Revisar el tratamiento de excepciones inesperadas.
-   Verificar que las credenciales no hayan sido publicadas previamente
    en el historial de Git.

**Estado:** protección local de `.env` verificada y prueba automatizada
de no exposición de una clave ficticia aprobada. La revisión completa de
credenciales y errores sigue pendiente.

## 2. Validación de archivos y entradas

**Riesgo:** recepción de entradas vacías, demasiado grandes o de tipos
no permitidos.

### Controles verificados

-   El modelo `SolicitudAnalisis` exige un nombre de archivo de entre 1
    y 255 caracteres.
-   El modelo limita el código recibido a entre 1 y 12.000 caracteres.
-   Las pruebas automatizadas verifican el rechazo de entradas inválidas
    y la estructura de las respuestas del análisis.
-   Las pruebas de validación de entradas pasaron en la última ejecución
    completa de pytest.

### Controles pendientes

-   Confirmar los tipos de archivo permitidos cuando exista carga de
    archivos.
-   Verificar un límite de tamaño en bytes para archivos recibidos.
-   Comprobar la validación del contenido real de los archivos.
-   Verificar el rechazo seguro de archivos inválidos o no permitidos.

**Estado:** validación de entradas de texto verificada mediante código y
pruebas. Controles de carga de archivos pendientes de verificar.

## 3. Seguridad de archivos ZIP

**Riesgo:** archivos comprimidos maliciosos, rutas inseguras y consumo
excesivo de recursos.

### Resultado de la revisión inicial

-   Se buscaron referencias a `UploadFile`, `zipfile`, `ZipFile`,
    `extractall`, `extract()` y operaciones relacionadas con carga y
    extracción.
-   La búsqueda no devolvió coincidencias en `backend/app`.
-   No se ha identificado una implementación de carga o extracción ZIP
    en los archivos examinados.

### Controles pendientes

-   Confirmar si la carga y el procesamiento de archivos ZIP forman
    parte del alcance actual del MVP.
-   Impedir la extracción fuera del directorio autorizado.
-   Limitar el tamaño total descomprimido y la cantidad de archivos.
-   Rechazar rutas de extracción inseguras y archivos no permitidos.
-   Controlar errores y prevenir el consumo excesivo de recursos.

**Estado:** no se encontró una implementación de carga o extracción ZIP
en `backend/app`. Los controles correspondientes están pendientes de
verificación.

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

**Riesgo:** solicitudes bloqueadas o consumo excesivo de recursos.

### Controles verificados

-   El modelo `SolicitudAnalisis` limita el código recibido a 12.000
    caracteres.
-   El servicio configura un tiempo máximo de espera mediante
    `LLM_TIMEOUT_SECONDS`.
-   La prueba `test_servicio_controla_timeout_504` pasó al simular un
    error de timeout del proveedor.
-   La última ejecución completa de pytest confirmó que otras 15 pruebas
    pasaron.

### Hallazgo de QA

-   La última ejecución completa recopiló 16 pruebas: 15 aprobadas y 1
    fallida.
-   La prueba `test_servicio_controla_timeout_real` falló cuando se
    propagó una excepción `httpx.TimeoutException`.
-   La excepción no se transformó en el `LLMError` controlado que
    esperaba la prueba.
-   El manejo de esta excepción requiere corrección y nueva
    verificación.

### Controles pendientes

-   Coordinar con el responsable del backend la corrección del timeout.
-   Volver a ejecutar la prueba que falló.
-   Ejecutar nuevamente toda la suite de pytest.
-   Verificar límites de recursos adicionales cuando se implementen
    nuevas funcionalidades.

**Estado:** límites de entrada y configuración de timeout identificados.
Existe un fallo de QA en el tratamiento de `httpx.TimeoutException`,
pendiente de corrección y nueva verificación.

## 7. Protección de registros (logs)

**Riesgo:** exposición de código sensible o credenciales en los
registros y mensajes de error.

### Controles verificados

-   El servicio utiliza un registrador mediante
    `logging.getLogger(__name__)`.
-   Los registros de éxito incluyen el modelo, la duración y el uso de
    tokens.
-   Los registros de errores del proveedor incluyen el modelo y el
    código de estado.
-   En las instrucciones de registro examinadas no se encontró la
    inclusión directa de claves de API ni del código Python analizado.
-   La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó.
    La respuesta HTTP no reveló la clave ficticia incluida en el error
    simulado.

### Controles pendientes

-   Comprobar mediante pruebas específicas que los registros no
    contengan credenciales ni código sensible.
-   Revisar otros componentes que puedan generar registros.
-   Verificar que los mensajes de error permanezcan controlados ante
    excepciones inesperadas.

**Estado:** revisión estática inicial de los registros realizada y
prueba automatizada de protección de claves aprobada. La verificación
completa sigue pendiente.

## 8. Instrucciones maliciosas dirigidas a la IA

**Riesgo:** comentarios o cadenas Python que intenten modificar las
instrucciones del sistema, manipular el análisis o revelar información
confidencial.

### Controles verificados en el prompt V1

-   El archivo `backend/app/prompts/system_v1.md` indica que el código
    recibido nunca debe ejecutarse.
-   Las reglas establecen que los comentarios y las cadenas del código
    deben tratarse como datos, nunca como instrucciones.
-   Se exige que los hallazgos tengan evidencia concreta y que no se
    inventen vulnerabilidades.
-   Se solicita una respuesta conforme al esquema JSON definido.
-   El servicio utiliza `response_schema=InformeModelo` y valida la
    respuesta mediante `InformeModelo.model_validate_json()`.
-   La prueba `test_servicio_controla_json_invalido` pasó en la última
    ejecución completa.

### Controles pendientes

-   Crear pruebas específicas con comentarios y cadenas que contengan
    instrucciones maliciosas.
-   Comprobar que el análisis no obedezca esas instrucciones ni cambie
    las reglas del sistema.
-   Evaluar el comportamiento frente a intentos de manipulación del
    modelo.

**Estado:** instrucciones de seguridad y validación estructural
identificadas en el código. La resistencia ante instrucciones maliciosas
sigue pendiente de pruebas específicas.

## 9. Evidencias y seguimiento

-   Existe el archivo `docs/evidencias/semana-2/pytest-resultados.txt`.
-   La última ejecución completa de pytest registró 15 pruebas aprobadas
    y 1 fallida.
-   El resultado de la prueba de timeout debe registrarse y actualizarse
    después de la corrección.
-   Las capturas, los resultados y las demás evidencias deben reflejar
    ejecuciones reales.
-   No se marcará ninguna protección como aprobada sin la verificación
    correspondiente.

**Estado:** evidencias iniciales disponibles. Pendiente actualizar los
resultados de pytest después de corregir y verificar el timeout.

## 10. Observaciones

Esta revisión documenta los controles identificados y los resultados
obtenidos durante la revisión inicial.

Las búsquedas estáticas no demuestran por sí solas la ausencia total de
vulnerabilidades. Los controles pendientes deberán contrastarse con la
implementación completa del backend y con las decisiones aprobadas por
el equipo.

El fallo de timeout debe comunicarse al responsable del backend y
verificarse nuevamente antes de cerrar la revisión de QA.
