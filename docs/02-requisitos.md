# 02. Requisitos y trazabilidad

Actualizado el 5 de noviembre de 2026 sobre `65675e2`. Historias reconstruidas
desde el producto y la rúbrica; no se presentan como entrevistas de Semana 1.
La aceptación por usuarios se registra en el [levantamiento](levantamiento.md).

## Requisitos funcionales

| ID | Requisito | Implementación | Verificación |
|---|---|---|---|
| RF-01 | Recibir código Python en JSON. | `POST /api/v1/analizar` | `test_analysis.py`, P05–P07 de producción |
| RF-02 | Recibir un archivo `.py`. | `POST /api/v1/archivos` | `test_uploads.py`, P08–P13 |
| RF-03 | Recibir un ZIP con hasta cinco `.py`. | `POST /api/v1/archivos/zip` | `test_uploads.py`, `test_zip_security_extra.py`, P14–P18 |
| RF-04 | Analizar un repositorio público de GitHub. | `POST /api/v1/repositorios/github` | `test_github.py`, P19–P23 |
| RF-05 | Entregar hallazgos estructurados con línea, severidad y corrección. | Modelos Pydantic y `analizar_codigo` | `test_analysis.py`, `test_llm.py` |
| RF-06 | Mostrar fuentes documentales. | RAG, `Fuente`, frontend | `test_rag_abstencion.py`, pruebas frontend |
| RF-07 | Abstenerse cuando no hay evidencia suficiente. | `InformeModelo`, validación de citas | `test_rag_abstencion.py` |
| RF-08 | Proporcionar inspección AST sin IA. | `/api/v1/agente/previsualizar` | `test_agente.py`, P24–P26 |
| RF-09 | Servir frontend y API desde el mismo origen. | Dockerfile y montaje `StaticFiles` | build, prueba de URL pública |
| RF-10 | Mostrar Ruff/Bandit con reglas y estado propios. | `/api/v1/estatico/analizar`, `StaticFindingsPanel` | `test_static_routes.py`, `test_static_analysis.py` |
| RF-11 | Conservar resultados parciales y exportarlos. | Respaldo estático y exportación JSON | `test_static_resilience.py`, pruebas frontend |
| RF-12 | Usar evidencia del agente en la revisión principal de un archivo. | `/api/v1/agente/analizar`, `AgentTracePanel` | `test_agente_integrado.py`, integración HTTP |

`RF-01` y `RF-02` describen endpoints directos que siguen disponibles. La interfaz principal utiliza `RF-12` para código y `.py`; ZIP/GitHub utilizan `RF-03`/`RF-04`. El modo demo no llama a Gemini ni acredita recuperación RAG.

## Historias de usuario y aceptación

| ID / necesidad | Dado | Cuando | Entonces | Trazabilidad |
|---|---|---|---|---|
| HU-01. Como desarrollador quiero revisar código pegado para localizar riesgos | Código Python dentro del límite y modo API | Solicito el análisis | Se muestra el informe y su estado real, con traza del agente; un error no se presenta como código seguro | RF-01, RF-12; `test_agente_integrado.py` |
| HU-02. Como desarrollador quiero cargar un `.py` para evitar copiarlo manualmente | Un archivo UTF-8 válido | Lo cargo y analizo | Se conserva el nombre y el agente procesa su texto sin ejecutarlo; una extensión inválida se rechaza | RF-02, RF-12; `test_uploads.py`, integración HTTP |
| HU-03. Como revisor quiero revisar un ZIP pequeño por archivo | Un ZIP permitido con hasta cinco `.py` | Solicito el análisis | Se separan informes y citas por archivo; traversal o exceso de archivos se rechazan | RF-03, RS-03; `test_zip_security_extra.py` |
| HU-04. Como revisor quiero analizar un repositorio público | URL HTTPS exacta `github.com/owner/repo` | Inicio la consulta | Se aplican límites de descarga y se presentan informes por archivo; dominios alternativos se rechazan | RF-04, RS-04; `test_github.py` |
| HU-05. Como evaluador quiero rastrear un hallazgo a su fuente | Un hallazgo contextual aceptado | Abro sus referencias | Cada ID se resuelve en las fuentes de ese informe; no se atribuyen citas de otro archivo | RF-06, RS-06; `test_rag_abstencion.py`, pruebas frontend |
| HU-06. Como usuario quiero conocer la falta de respaldo | No hay documentación suficiente o todas las citas son inválidas | Finaliza el análisis | Se comunica abstención y su motivo, sin afirmar ausencia de vulnerabilidades | RF-07; `test_rag_abstencion.py` |
| HU-07. Como QA quiero inspeccionar código sin proveedor generativo | Código válido con comentarios que intentan dar instrucciones | Uso previsualización AST | Solo se inspecciona la sintaxis; no se ejecutan las instrucciones ni el programa | RF-08, RS-01, RS-05; `test_agente.py`, P26 |
| HU-08. Como usuario quiero distinguir alertas estáticas de IA | Ruff/Bandit devuelven resultados | Abro el panel estático | Veo herramienta, regla, ubicación y estado, con severidad/confianza si existen; no se inventan fuentes OWASP/MITRE | RF-10; `test_static_routes.py`, pruebas frontend |
| HU-09. Como usuario quiero conservar resultados útiles ante un fallo | Gemini falla y existe resultado estático aprovechable | Finaliza la petición | El informe indica `parcial` y mantiene las alertas; no muestra una aprobación de seguridad | RF-11; `test_static_resilience.py` |
| HU-10. Como evaluador quiero exportar el análisis para revisarlo | Hay un resultado completo, parcial o abstenido | Descargo JSON | Se conservan estado, fuentes, resultados estáticos y traza cuando estén presentes | RF-06, RF-11, RF-12; integración HTTP y exportación frontend |
| HU-11. Como usuario quiero proteger mis datos en errores | Entrada inválida con un marcador sensible | La API responde 422 | No devuelve `input`, `ctx`, código ni el marcador | RS-07, RS-09; `test_validation_privacy.py`, P07 |
| HU-12. Como operador quiero conservar el conocimiento tras reiniciar | Índice en volumen persistente y baseline guardado | Reinicio sin borrar el volumen y repito la consulta | Se compara la continuidad de citas y se conserva el log de recuperación, sin confundirlo con una auditoría completa del volumen | RNF-02; evidencia antes/después del 5 de noviembre |

## Requisitos de seguridad

| ID | Requisito | Criterio de aceptación |
|---|---|---|
| RS-01 | No ejecutar código recibido como programa. | No se invocan `exec`, `eval` ni imports del payload. Ruff/Bandit son procesos de análisis autorizados y pueden leer un archivo temporal; eso no ejecuta el programa analizado. |
| RS-02 | Limitar recursos de entrada. | Rechazar tamaños, caracteres, entradas ZIP y cantidades superiores a lo permitido. |
| RS-03 | Evitar ZIP traversal y entradas especiales. | Rechazar rutas absolutas, `..`, barras invertidas, duplicados, enlaces y ZIP cifrados. |
| RS-04 | Evitar SSRF en GitHub. | Aceptar solo URL HTTPS exacta `github.com/owner/repo`; usar `api.github.com` sin redirecciones. |
| RS-05 | Resistir instrucciones en código y documentos. | Serializar ambos como datos no confiables; mantener instrucciones del sistema separadas. |
| RS-06 | No inventar citas. | Cada referencia del modelo debe existir entre los fragmentos recuperados. |
| RS-07 | Proteger secretos y datos sensibles. | `.env` no rastreado ni copiado; logs y errores no muestran claves o código. |
| RS-08 | Controlar errores externos. | En el flujo directo, 429 del proveedor se traduce a 503 y timeout a 504; si hay respaldo estático útil puede responder 200 `parcial`. El 429 de la protección local es distinto. Ver contrato de resiliencia. |
| RS-09 | No reflejar payloads en errores de validación. | El 422 conserva tipo, ubicación y mensaje, pero elimina `input` y `ctx`. |

## Requisitos no funcionales

| ID | Requisito | Criterio |
|---|---|---|
| RNF-01 | Reproducibilidad | Dockerfile multi-stage, versiones fijadas y comandos documentados. |
| RNF-02 | Persistencia | ChromaDB en `/data/chroma` sobre volumen; citas disponibles después del reinicio. |
| RNF-03 | Disponibilidad observable | `/health` responde sin exponer configuración. |
| RNF-04 | Trazabilidad | Pruebas, métricas y evidencias identifican fecha, objetivo y alcance. |
| RNF-05 | Usabilidad | Interfaz responsive con estados de carga, error, abstención y fuentes. |
| RNF-06 | Despliegue seguro | Proceso de aplicación UID 10001 en Docker; `no-new-privileges` en Compose; secretos en ejecución y HTTPS proporcionado por Railway. No extrapolar opciones Compose a Railway. |

### Umbrales medibles y método de comprobación

Son límites implementados, no una promesa de disponibilidad ni latencia comercial. La evidencia ejecutada se consulta en [pruebas](08-pruebas.md).

| ID | Umbral o resultado observable | Verificación |
|---|---|---|
| RNF-07 | Código: máximo 12.000 caracteres; `.py`: máximo 1 MiB y además 12.000 caracteres | `services/files.py`, `test_uploads.py`, P13 |
| RNF-08 | ZIP: máximo 5 MiB comprimidos, 20 MiB declarados descomprimidos, 100 entradas, cinco `.py` y 12.000 caracteres Python acumulados | `services/zip_files.py`, `test_zip_security_extra.py` |
| RNF-09 | GitHub: hasta cinco archivos, 48.000 bytes por archivo y 12.000 caracteres acumulados | `services/github_repos.py`, `test_github.py` |
| RNF-10 | Ruff/Bandit: timeout de 12 s por herramienta y captura conjunta stdout/stderr limitada a 1.000.000 bytes por proceso | `services/static_analysis.py`, `test_static_output_limits.py`; no es límite de memoria total |
| RNF-11 | Agente: hasta tres inspecciones, veinte indicadores por inspección y cuarenta reglas en la evidencia de síntesis | `services/evidencia.py`, `test_agente_integrado.py`; la respuesta conserva la lista estática completa |
| RNF-12 | Errores 422: cero apariciones del marcador sensible de prueba en la respuesta | `test_validation_privacy.py`, P07 |
| RNF-13 | Producción: al menos 15 escenarios; la matriz actual contiene 26 aserciones de escenarios | Evidencia pública 26/26; no mide resistencia completa de Gemini a prompt injection |
| RNF-14 | Instalación por un integrante nuevo en no más de 10 minutos | Objetivo de la rúbrica pendiente de prueba cronometrada; registrar equipo, cachés, inicio, fin y resultado |
| RNF-15 | Interfaz legible a 390 px y 1440 px, con estado y origen visibles | Objetivo de revisión visual; conservar la revisión evaluada. Las capturas anteriores no certifican automáticamente el panel integrado del PR #31 |

## Restricciones y supuestos

- El lenguaje soportado es Python.
- Solo se consultan repositorios públicos pequeños.
- ChromaDB funciona embebido con una única réplica/proceso.
- Gemini requiere clave, modelo y cuota válidos.
- HTTPS y reinicio remoto dependen de la plataforma de hosting.
- La URL pública no se considera entregada hasta ejecutarse la matriz de producción y guardar evidencia.

La matriz ya tiene evidencia pública para la revisión documentada. Una nueva fusión a `main` no prueba por sí sola que Railway sirva ese SHA.

## Criterio de cierre

Un requisito se marca como aprobado únicamente cuando existe una prueba ejecutada y su evidencia. La existencia de código o de un caso automatizado sin ejecutar no demuestra por sí sola el cumplimiento en producción.
