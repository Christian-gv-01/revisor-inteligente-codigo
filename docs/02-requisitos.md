# 02. Requisitos y trazabilidad

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

## Requisitos de seguridad

| ID | Requisito | Criterio de aceptación |
|---|---|---|
| RS-01 | No ejecutar código recibido. | No se crean archivos ni se invocan `exec`, `eval`, imports o procesos sobre el payload. |
| RS-02 | Limitar recursos de entrada. | Rechazar tamaños, caracteres, entradas ZIP y cantidades superiores a lo permitido. |
| RS-03 | Evitar ZIP traversal y entradas especiales. | Rechazar rutas absolutas, `..`, barras invertidas, duplicados, enlaces y ZIP cifrados. |
| RS-04 | Evitar SSRF en GitHub. | Aceptar solo URL HTTPS exacta `github.com/owner/repo`; usar `api.github.com` sin redirecciones. |
| RS-05 | Resistir instrucciones en código y documentos. | Serializar ambos como datos no confiables; mantener instrucciones del sistema separadas. |
| RS-06 | No inventar citas. | Cada referencia del modelo debe existir entre los fragmentos recuperados. |
| RS-07 | Proteger secretos y datos sensibles. | `.env` no rastreado ni copiado; logs y errores no muestran claves o código. |
| RS-08 | Controlar errores externos. | 429 se transforma en 503; timeout en 504; otros errores en 502. |
| RS-09 | No reflejar payloads en errores de validación. | El 422 conserva tipo, ubicación y mensaje, pero elimina `input` y `ctx`. |

## Requisitos no funcionales

| ID | Requisito | Criterio |
|---|---|---|
| RNF-01 | Reproducibilidad | Dockerfile multi-stage, versiones fijadas y comandos documentados. |
| RNF-02 | Persistencia | ChromaDB en `/data/chroma` sobre volumen; citas disponibles después del reinicio. |
| RNF-03 | Disponibilidad observable | `/health` responde sin exponer configuración. |
| RNF-04 | Trazabilidad | Pruebas, métricas y evidencias identifican fecha, objetivo y alcance. |
| RNF-05 | Usabilidad | Interfaz responsive con estados de carga, error, abstención y fuentes. |
| RNF-06 | Despliegue seguro | Usuario no privilegiado, `no-new-privileges`, secretos solo en ejecución y HTTPS del proveedor. |

## Restricciones y supuestos

- El lenguaje soportado es Python.
- Solo se consultan repositorios públicos pequeños.
- ChromaDB funciona embebido con una única réplica/proceso.
- Gemini requiere clave, modelo y cuota válidos.
- HTTPS y reinicio remoto dependen de la plataforma de hosting.
- La URL pública no se considera entregada hasta ejecutarse la matriz de producción y guardar evidencia.

## Criterio de cierre

Un requisito se marca como aprobado únicamente cuando existe una prueba ejecutada y su evidencia. La existencia de código o de un caso automatizado sin ejecutar no demuestra por sí sola el cumplimiento en producción.
