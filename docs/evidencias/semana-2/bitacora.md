
# Bitácora de QA, Seguridad y Documentación

**Proyecto:** Revisor Inteligente de Código Seguro
**Rama:** `feature/qa-seguridad`
**Fecha de inicio:** 20 de octubre de 2026
**Última actualización:** 22 de octubre de 2026
**Estado:** En progreso; 42 pruebas aprobadas y documentación pendiente de revisión final


## 1. Pruebas automatizadas

### 1.1. Endpoint de salud

- Se creó `backend/tests/test_health.py`.
- Se verificó el endpoint `GET /health` mediante `TestClient`.
- La prueba `test_health_endpoint_returns_success` pasó en las ejecuciones registradas.

### 1.2. Análisis y validación de entradas

- Se creó `backend/tests/test_analysis.py`.
- Se verificó la estructura de la respuesta JSON del endpoint `POST /api/v1/analizar`.
- Se ejecutaron seis escenarios parametrizados de entradas inválidas: código vacío, código ausente, nombre de archivo vacío, nombre ausente, nombre demasiado largo y código demasiado largo.
- Se comprobó que las solicitudes inválidas reciben HTTP 422 sin invocar el servicio de IA simulado.
- Se verificó la conversión de un error controlado del servicio en una respuesta HTTP adecuada.
- Las pruebas correspondientes pasaron en la última ejecución parcial registrada.

### 1.3. Servicio de inteligencia artificial

Se creó `backend/tests/test_llm.py` y se incorporaron pruebas con mocks del cliente de Gemini para verificar:

- Respuesta JSON válida.
- Respuesta vacía del modelo.
- Error HTTP 429 del proveedor, transformado en error controlado.
- Error HTTP 504 del proveedor, transformado en error controlado.
- Respuesta JSON inválida.
- Que una respuesta HTTP no revele una clave ficticia incluida en el error simulado del proveedor.
- Que se rechace un hallazgo cuyo número de línea no existe en el código recibido.
- Que los comentarios y cadenas con instrucciones maliciosas se envíen como contenido para analizar, manteniendo el prompt del sistema.
- Que, en un error simulado, los logs capturados no incluyan una clave ni código sensible ficticios.

Las tres últimas pruebas añadidas (`test_servicio_rechaza_linea_inexistente`, `test_servicio_trata_codigo_malicioso_como_datos` y `test_servicio_no_registra_claves_ni_codigo_sensible`) pasaron individualmente y en la ejecución parcial más reciente.

**Limitación:** la prueba de instrucciones maliciosas verifica el contrato del servicio con un modelo simulado; no demuestra resistencia exhaustiva de Gemini frente a *prompt injection*. La prueba de logs cubre el escenario simulado, no todos los componentes ni las excepciones posibles.

### 1.4. Resultado histórico: ejecución completa de 16 pruebas

Antes de incorporar las tres pruebas adicionales, se ejecutó la suite completa y se obtuvo:

- **16 pruebas recopiladas.**
- **15 pruebas aprobadas.**
- **1 prueba fallida:** `test_servicio_controla_timeout_real`.

La prueba simula una excepción `httpx.TimeoutException` y espera que `analizar_codigo()` la transforme en `LLMError` con código HTTP 504. La excepción se propagó sin transformarse en el error controlado esperado.

Este resultado se conserva como un hallazgo real de QA; no se ha marcado la prueba como aprobada.

### 1.5. Resultado histórico: ejecución parcial de 19 pruebas recopiladas

Después de incorporar las tres pruebas nuevas, se ejecutó desde la carpeta `backend`:

```powershell
python -m pytest tests -v -k "not test_servicio_controla_timeout_real"
```

**Resultado observado:**

- **19 pruebas recopiladas.**
- **18 pruebas ejecutadas y aprobadas.**
- **1 prueba excluida:** `test_servicio_controla_timeout_real`.
- **Código de salida del comando: 0.**

La evidencia se guardó en `docs/evidencias/semana-2/pytest-resultados.txt`. Esta ejecución demuestra que pasan los 18 casos seleccionados, pero **no acredita que la suite completa de 19 pruebas esté aprobada**.

### 1.6. Observaciones de ejecución

- Una ejecución anterior desde la raíz del proyecto produjo `ModuleNotFoundError: No module named 'app'`; las pruebas se ejecutaron desde la carpeta `backend` para utilizar correctamente los imports.
- Se observó anteriormente una advertencia de compatibilidad relacionada con `TestClient` y HTTPX; requiere seguimiento si reaparece.
- Las pruebas utilizan mocks para no consumir la API de Gemini ni depender de Internet en los escenarios simulados.

## 2. Documentación técnica

- Se creó y actualizó `docs/03-arquitectura.md` para reflejar la API FastAPI, el endpoint de análisis, la integración examinada con Gemini y los componentes pendientes de validación.
- Se creó y actualizó `docs/09-decisiones.md` con ADR-001 a ADR-004, distinguiendo implementación técnica y aprobación definitiva del equipo.
- Se actualizó `docs/revision-seguridad.md` con controles identificados, hallazgos y pendientes.
- Se creó y publicó el README principal mediante el commit `04bab7c` (`docs: completar README inicial`).
- La arquitectura y las decisiones definitivas siguen pendientes de validación por el equipo.

## 3. Revisión de seguridad

### 3.1. Credenciales y variables de entorno

- Se revisó `.gitignore` y se comprobó que excluye `.env` y `.env.*`, permitiendo `.env.example`.
- `git check-ignore -v .env` confirmó la regla que ignora `.env`.
- `git ls-files -- .env` no devolvió rutas: el archivo no estaba registrado en el índice consultado.
- El contenido revisado de `.env.example` no incluía valores de claves reales.
- El servicio examinado obtiene `GEMINI_API_KEY` mediante una variable de entorno.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó con una clave ficticia en un error simulado.

**Pendiente:** revisar posibles secretos en el historial y ampliar las verificaciones de errores y registros. Estas comprobaciones no son una auditoría exhaustiva de secretos.

### 3.2. Validación de entradas

- El modelo `SolicitudAnalisis` exige un nombre de archivo de entre 1 y 255 caracteres.
- El campo `codigo` admite entre 1 y 12.000 caracteres.
- Las pruebas de validación comprobaron el rechazo de entradas ausentes, vacías o demasiado largas.

**Pendiente:** verificar tipos, contenido y tamaños en bytes si se implementa carga de archivos.

### 3.3. Archivos ZIP y carga de archivos

- Una búsqueda en los archivos examinados de `backend/app` no encontró las referencias consultadas a carga y extracción de ZIP.
- No se confirmó una implementación de carga o extracción ZIP en esa revisión.

**Pendiente:** confirmar el alcance del MVP; si se incorpora esta funcionalidad, verificar rutas seguras, tipos, cantidad de archivos, tamaños descomprimidos y límites de recursos.

### 3.4. Repositorios autorizados

- Una búsqueda estática en los archivos Python examinados de `backend/app` no encontró referencias consultadas a repositorios, validación de URL o direcciones internas.
- No se confirmó una funcionalidad de consulta o descarga de repositorios en esa revisión.

**Pendiente:** confirmar si se incorporará al MVP y, en tal caso, verificar dominios y repositorios permitidos, redirecciones y prevención de acceso a direcciones internas.

### 3.5. Aislamiento del código recibido

- Se buscaron referencias a `exec()`, `eval()`, `compile()`, `__import__()`, `importlib`, `subprocess`, `runpy` y `os.system` en los archivos Python examinados de `backend/app`, sin coincidencias.
- El servicio de IA examinado envía el código recibido como contenido destinado al análisis.
- El prompt V1 indica no ejecutar código y tratar comentarios y cadenas como datos.
- La prueba `test_servicio_trata_codigo_malicioso_como_datos` pasó con un cliente simulado.

**Pendiente:** revisar integralmente posibles vías indirectas de ejecución y evaluar ataques reales de manipulación de instrucciones. Una búsqueda textual no equivale a una garantía de aislamiento.

### 3.6. Límites de tiempo y recursos

- Existe un límite de 12.000 caracteres para el código recibido.
- El servicio lee `LLM_TIMEOUT_SECONDS` para configurar la espera del cliente del proveedor.
- La prueba de error HTTP 504 del proveedor pasó.
- **Hallazgo corregido:** `test_servicio_controla_timeout_real` pasó después de integrar la corrección del backend. Una ejecución intermedia obtuvo 40 aprobadas y 0 fallidas; la ejecución completa más reciente registró 44 aprobadas y 0 fallidas.

**Verificación:** QA confirmó la corrección con la prueba específica de timeout y una ejecución completa de la suite.

### 3.7. Logs y mensajes de error

- Se revisaron las llamadas a `logging` del servicio de IA.
- Los registros examinados incluyen modelo, duración, consumo de tokens y estado del proveedor, sin registrar directamente el código analizado ni la clave en las llamadas observadas.
- La prueba `test_endpoint_no_expone_clave_en_error_proveedor` pasó.
- La prueba `test_servicio_no_registra_claves_ni_codigo_sensible` pasó en el escenario simulado.

**Pendiente:** ampliar las pruebas a otros errores, componentes y configuraciones de logs.

### 3.8. Instrucciones maliciosas dirigidas a la IA

- Se revisó `backend/app/prompts/system_v1.md`.
- El prompt ordena tratar comentarios y cadenas como datos, no como instrucciones.
- El servicio valida las respuestas mediante el modelo `InformeModelo`.
- Las pruebas `test_servicio_controla_json_invalido` y `test_servicio_trata_codigo_malicioso_como_datos` pasaron.

**Pendiente:** comprobar la resistencia real del modelo a intentos de *prompt injection*; los mocks no prueban la conducta del proveedor externo.

## 4. Evidencias

- `docs/evidencias/semana-2/pytest-resultados.txt` contiene la ejecución completa más reciente: **44 aprobadas y 0 fallidas**.
- La ejecución completa anterior de 16 pruebas produjo **15 aprobadas y 1 fallida**; este resultado histórico se conserva documentado en la bitácora.
- La ejecución parcial anterior excluyó la prueba de timeout; una ejecución completa posterior confirmó que pasó.
- Las capturas y resultados deben corresponder a ejecuciones reales; no se inventarán aprobaciones ni resultados.
- **Pendiente:** ejecutar toda la suite tras la corrección, actualizar evidencias, registrar el historial de commits relevante y completar las pruebas de las versiones de prompts que el equipo haya implementado realmente.

## 5. Estado del README

El README principal se creó en la raíz del repositorio y se publicó en `feature/qa-seguridad` mediante el commit `04bab7c`.

Debe mantenerse alineado con los endpoints y funcionalidades reales, las variables de entorno necesarias, la ejecución de pruebas y las limitaciones actuales del MVP.

## 6. Estado de los documentos técnicos

- `docs/03-arquitectura.md`: actualizado; pendiente de validación por el equipo.
- `docs/09-decisiones.md`: actualizado; ADR pendientes de aprobación definitiva.
- `docs/revision-seguridad.md`: actualizado con la revisión inicial y los controles pendientes; verificar su coherencia con las últimas pruebas en el cierre final.
- `docs/evidencias/semana-2/bitacora.md`: actualizado con tres pruebas adicionales y la ejecución parcial de 19 casos recopilados.
- `docs/evidencias/semana-2/pytest-resultados.txt`: actualizado con el resultado de 42 pruebas aprobadas y 0 fallidas.

## 7. Próximos pasos

1. Verificar que la arquitectura documente los límites de carga Python y ZIP.
2. Revisar los ADR-001 a ADR-004 y confirmar las decisiones aprobadas por el equipo.
3. Actualizar la revisión de seguridad y comprobar las evidencias de los prompts.
4. Revisar que los cambios locales incluyan solo archivos de QA y documentación antes del siguiente commit.
5. Validar las decisiones arquitectónicas y las funciones pendientes con los demás integrantes.
6. Revisar el pull request de `feature/qa-seguridad` y preparar las evidencias para la entrega.

## 8. Observaciones

- Los resultados corresponden a las comprobaciones compartidas y ejecutadas durante esta semana.
- El resultado de 18 aprobadas y 1 excluida es histórico. Una ejecución intermedia registró 40 aprobadas y 0 fallidas; la ejecución completa más reciente registró 44 aprobadas y 0 fallidas.
- Las pruebas con mocks comprueban comportamientos específicos del sistema sin conectarse a Gemini; no acreditan por sí mismas la calidad o seguridad de las respuestas reales del modelo.
- Ninguna protección pendiente se considerará completamente verificada sin evidencia suficiente.

## 9. Actualización del jueves 22 de octubre de 2026

### 9.1. Integración del backend

- Se integraron cambios de la rama `feature/backend-ia` en `feature/qa-seguridad`.
- El merge quedó registrado en el commit `d7e5f69`.
- La integración incorpora los servicios de carga de archivos Python y análisis de proyectos ZIP.
- La prueba `test_servicio_controla_timeout_real` pasó después de integrar la corrección del timeout.

### 9.2. Pruebas de carga de archivos

- Se incorporó `backend/tests/test_uploads.py`.
- La ejecución actual de las pruebas de carga Python y ZIP registró 25 pruebas aprobadas, incluidas las dos variantes de regresión de descompresión.
- Se comprobaron extensiones no permitidas, rutas inseguras, contenido vacío, UTF-8 inválido, bytes nulos y límites de tamaño.
- Se probaron ZIP corruptos, rutas peligrosas, límites de archivos y caracteres acumulados, y errores controlados del servicio de IA.
- Se utilizaron mocks para evitar llamadas reales al proveedor durante las pruebas.

### 9.3. Resultado de la suite completa

- Comando ejecutado: `python -m pytest tests -v`.
- Directorio de ejecución: `backend`.
- Resultado: 44 pruebas aprobadas y 0 fallidas.
- Duración registrada: 1,72 segundos.
- La salida se guardó en `docs/evidencias/semana-2/pytest-resultados.txt`.
- El resultado anterior que contenía un fallo de timeout queda como antecedente histórico; la ejecución posterior confirmó que esa prueba también pasó.

### 9.4. Pendientes de documentación y entrega

- Revisar la arquitectura para reflejar la carga de Python y ZIP implementada.
- Verificar los ADR-001 a ADR-004 y distinguir las decisiones aprobadas de las pendientes de confirmación.
- Actualizar la revisión de seguridad con los controles comprobados y las limitaciones restantes.
- Verificar las evidencias de las tres versiones de prompts y las capturas requeridas.
- Revisar los cambios de Git antes de preparar el siguiente commit y subir la rama.
- Mantener pendiente la revisión del Pull Request por el equipo.
