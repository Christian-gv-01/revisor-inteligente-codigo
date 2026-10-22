# Bitácora de QA, Seguridad y Documentación

**Proyecto:** Revisor Inteligente de Código Seguro
**Rama:** `feature/qa-seguridad`
**Fecha de inicio:** 20 de octubre de 2026
**Última actualización:** 21 de octubre de 2026
**Estado:** En progreso

## 1. Pruebas automatizadas

### 1.1. Endpoint de salud

- Se creó `backend/tests/test_health.py`.
- Se verificó el endpoint `GET /health` mediante `TestClient`.
- La prueba `test_health_endpoint_returns_success` pasó en las ejecuciones registradas.

### 1.2. Análisis y validación de entradas

- Se creó `backend/tests/test_analysis.py`.
- Se incorporaron pruebas para verificar respuestas JSON válidas, entradas inválidas y tratamiento de errores del servicio.
- Las pruebas de esta suite pasaron en la última ejecución completa registrada.

### 1.3. Servicio de inteligencia artificial

- Se creó `backend/tests/test_llm.py`.
- Se probaron respuestas válidas, respuestas vacías, errores del proveedor, timeouts y respuestas JSON inválidas.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó al simular un error que contenía una clave ficticia.
- La prueba `test_servicio_controla_timeout_504` pasó en la última ejecución completa registrada.
- La prueba `test_servicio_controla_timeout_real` falló porque se propagó una excepción `httpx.TimeoutException` en lugar del error controlado esperado.

### 1.4. Resultado de la última ejecución completa

**Resultado registrado: 16 pruebas ejecutadas, 15 aprobadas y 1 fallida.**

La prueba pendiente de corrección es:

`test_servicio_controla_timeout_real`

El servicio debe transformar la excepción de timeout en un error controlado con el mensaje esperado y el código HTTP correspondiente.

El fallo se debe comunicar al responsable del backend. Después de corregirlo, deberá ejecutarse nuevamente la suite completa.

### 1.5. Observaciones sobre la ejecución

- La ejecución inicial desde la raíz del proyecto produjo `ModuleNotFoundError: No module named 'app'`.
- Las pruebas se ejecutaron correctamente desde la carpeta `backend`, donde se encuentra el contexto de importación de la aplicación.
- Se observó una advertencia de compatibilidad relacionada con `TestClient` y HTTPX. Su revisión continúa pendiente.

## 2. Documentación técnica

- Se creó `docs/03-arquitectura.md` y posteriormente se actualizó para reflejar el backend implementado y diferenciar los componentes pendientes.
- Se creó `docs/09-decisiones.md` y se actualizaron las decisiones arquitectónicas para distinguir las implementaciones identificadas de las propuestas pendientes de aprobación.
- Se actualizó `docs/revision-seguridad.md` para incorporar los resultados de las verificaciones realizadas y los hallazgos pendientes.
- El README principal se publicó mediante el commit `04bab7c`, con el mensaje `docs: completar README inicial`.
- Las decisiones arquitectónicas definitivas deben confirmarse con los responsables correspondientes.

## 3. Revisión de seguridad

### 3.1. Credenciales y variables de entorno

- Se revisó `.gitignore`.
- Se comprobó que las reglas excluyen `.env` y `.env.*`, con una excepción para `.env.example`.
- `git check-ignore -v .env` confirmó que Git ignora `.env`.
- `git ls-files -- .env` no devolvió resultados.
- Se revisó `.env.example` y no se identificaron valores de claves reales en el contenido examinado.
- Se comprobó que el servicio obtiene `GEMINI_API_KEY` desde una variable de entorno.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó con una clave ficticia en un error simulado.

Estas comprobaciones no constituyen una auditoría completa del historial de Git ni una búsqueda exhaustiva de secretos en todos los archivos.

### 3.2. Validación de entradas

- Se revisó el modelo `SolicitudAnalisis`.
- El nombre de archivo tiene un límite de entre 1 y 255 caracteres.
- El código recibido tiene un límite de entre 1 y 12.000 caracteres.
- Las pruebas automatizadas de validación de entradas pasaron en la última ejecución completa registrada.

La carga de archivos y la validación de su contenido real siguen pendientes de confirmar.

### 3.3. Archivos ZIP y carga de archivos

- Se buscaron referencias a `UploadFile`, `zipfile`, `ZipFile`, `extractall`, `extract()` y operaciones relacionadas con carga y extracción.
- No se encontraron coincidencias en los archivos examinados de `backend/app`.
- No se ha identificado una implementación de carga o extracción ZIP en ese directorio.

Queda pendiente confirmar si estas funcionalidades forman parte del alcance del MVP. Si se incorporan, deberán verificarse los límites de tamaño, la cantidad de archivos y la seguridad de las rutas de extracción.

### 3.4. Repositorios autorizados

- Se buscaron referencias a GitHub, repositorios, solicitudes HTTP, validación de URL y direcciones IP en los archivos Python examinados de `backend/app`.
- La búsqueda no devolvió coincidencias.
- No se ha confirmado una implementación de descarga o consulta de repositorios en los archivos revisados.

La funcionalidad y sus controles de acceso quedan pendientes de confirmar con el equipo.

### 3.5. Aislamiento del código recibido

- Se buscaron referencias a `exec()`, `eval()`, `compile()`, `__import__()`, `importlib`, `subprocess`, `runpy` y `os.system` en los archivos Python examinados de `backend/app`.
- La búsqueda no devolvió coincidencias.
- El prompt `backend/app/prompts/system_v1.md` establece que el código recibido no debe ejecutarse y que los comentarios y las cadenas deben tratarse como datos.
- El servicio envía el código al proveedor para su análisis y valida estructuralmente la respuesta.

Las búsquedas estáticas no demuestran por sí solas la ausencia total de vulnerabilidades. Quedan pendientes pruebas específicas contra instrucciones maliciosas y una verificación completa del aislamiento.

### 3.6. Límites de tiempo y recursos

- El modelo de entrada limita el código a 12.000 caracteres.
- El servicio configura un tiempo máximo de espera mediante `LLM_TIMEOUT_SECONDS`.
- La prueba `test_servicio_controla_timeout_504` pasó.
- La prueba `test_servicio_controla_timeout_real` falló por la propagación de `httpx.TimeoutException`.

**Hallazgo de QA pendiente:** revisar el manejo de esta excepción con el responsable del backend, repetir la prueba afectada y ejecutar nuevamente toda la suite.

### 3.7. Logs y mensajes de error

- Se revisó el uso de `logging` en el servicio de IA.
- Los registros examinados incluyen el modelo, la duración, el uso de tokens y el código de estado del proveedor.
- No se encontró la inclusión directa de claves de API ni del código analizado en las instrucciones de registro examinadas.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó.

Queda pendiente completar las pruebas específicas de los registros y revisar el tratamiento de excepciones inesperadas.

### 3.8. Instrucciones maliciosas dirigidas a la IA

- Se revisó el prompt V1.
- Las instrucciones indican que el código recibido no debe ejecutarse y que los comentarios y las cadenas no deben obedecerse como instrucciones.
- El servicio valida la respuesta mediante `InformeModelo`.
- La prueba `test_servicio_controla_json_invalido` pasó en la última ejecución completa registrada.

Quedan pendientes las pruebas específicas con comentarios y cadenas maliciosas y la evaluación de intentos de manipulación del modelo.

## 4. Evidencias

- Existe `docs/evidencias/semana-2/pytest-resultados.txt`.
- La última ejecución completa registrada contiene 16 pruebas: 15 aprobadas y 1 fallida.
- El fallo de timeout debe mantenerse documentado hasta que se corrija y verifique.
- Se deben conservar capturas y resultados que correspondan a ejecuciones reales.
- Queda pendiente actualizar la evidencia de pytest después de la corrección del backend.
- Deben registrarse las decisiones del equipo y las soluciones aplicadas a los hallazgos.

## 5. Estado del README

El README principal se creó en la raíz del repositorio y se publicó en `feature/qa-seguridad` mediante el commit `04bab7c`.

Su contenido debe mantenerse alineado con las funcionalidades reales, las instrucciones de ejecución, las variables de entorno, las pruebas y las limitaciones actuales del sistema.

## 6. Estado de los documentos técnicos

- `docs/03-arquitectura.md`: actualizado; pendiente de validación por el equipo.
- `docs/09-decisiones.md`: actualizado; aprobación definitiva de las decisiones pendiente.
- `docs/revision-seguridad.md`: actualizado con verificaciones iniciales y hallazgos pendientes.
- `docs/evidencias/semana-2/bitacora.md`: en actualización para reflejar los resultados y tareas recientes.
- `docs/evidencias/semana-2/pytest-resultados.txt`: contiene el resultado de la ejecución registrada.

## 7. Próximos pasos

1. Coordinar con el responsable del backend la corrección de `httpx.TimeoutException`.
2. Repetir la prueba de timeout y ejecutar la suite completa.
3. Actualizar las evidencias con los resultados reales.
4. Completar las pruebas de seguridad pendientes.
5. Validar la arquitectura y las decisiones con el equipo.
6. Revisar todos los cambios de Git.
7. Preparar el commit y el Pull Request cuando los cambios estén revisados y el estado de las pruebas esté documentado.

## 8. Observaciones

Los resultados registrados corresponden a las ejecuciones y comprobaciones realizadas hasta la fecha.

Las búsquedas estáticas y las pruebas parciales no demuestran por sí solas que el sistema esté completamente libre de vulnerabilidades.

Ningún control de seguridad ni prueba pendiente se considerará aprobado hasta que exista evidencia suficiente de su implementación y funcionamiento.
