# 08. Plan y resultados de pruebas — Entrega 4

> Actualización del cierre del 7 de noviembre: P25 rechaza cinco pasos porque el máximo es cuatro.
> La [matriz pública vigente](evidencias/semana-4/revision7-cierre-20261107/matriz-publica-3214960.json)
> registra una ejecución nueva, sin Gemini, antes del cambio de ruta de la interfaz.
> Las pruebas de proveedor y generación real se enlazan desde [docs/37](37-cierre-verificado.md).
> Los conteos que siguen conservan sus revisiones históricas.

> Resultado público histórico posterior a la integración: **26/26 aprobadas** y análisis con tres fuentes. Ver [15-verificacion-publica-integrada.md](15-verificacion-publica-integrada.md). La continuidad de citas tras el reinicio posterior y el log de recuperación del índice se documentan en [el cierre consolidado](12-cierre-qa-entrega4.md); no constituyen una auditoría completa del volumen.

## Alcance

Este documento cubre el rol de QA, seguridad y documentación. Separa tres niveles:

1. Pruebas unitarias e integración con servicios externos simulados.
2. Pruebas HTTP contra una instancia local equivalente.
3. Pruebas contra la URL pública HTTPS, con ejecuciones y alcances registrados por separado.

No se convierten resultados locales en evidencia pública ni se presentan mocks como respuestas reales de Gemini.

## Matriz de producción

El ejecutor `scripts/pruebas_produccion.py` contiene 26 escenarios y genera JSON verificable.

| ID | Área | Escenario | Resultado esperado |
|---|---|---|---|
| P01 | Disponibilidad | `/health` | 200, `status=ok` |
| P02 | Disponibilidad | OpenAPI | 200 y rutas publicadas |
| P03 | Errores | Ruta inexistente | 404 |
| P04 | Errores | Método no permitido | 405 |
| P05 | Validación | JSON ausente | 422 sanitizado |
| P06 | Validación | Código vacío | 422 |
| P07 | Secretos | Código excesivo con marcador | 422 sin reflejar marcador |
| P08 | Archivo | Extensión `.txt` | 400 |
| P09 | Archivo | Nombre con traversal | 400 |
| P10 | Archivo | `.py` vacío | 400 |
| P11 | Archivo | Byte nulo | 400 |
| P12 | Archivo | Codificación inválida | 400 |
| P13 | Archivo | Más de 12.000 caracteres | 413 |
| P14 | ZIP | ZIP corrupto | 400 |
| P15 | ZIP | Ruta `../` | 400 |
| P16 | ZIP | Seis archivos Python | 413 |
| P17 | ZIP | Sin Python | 400 |
| P18 | ZIP | Python binario | 400 |
| P19 | GitHub | URL sin HTTPS | 400 |
| P20 | GitHub | Dominio engañoso | 400 |
| P21 | GitHub | Query sensible | 400 |
| P22 | GitHub | Ruta adicional | 400 |
| P23 | GitHub | Loopback | 400 |
| P24 | Agente | Nombre traversal | 422 |
| P25 | Agente | Cinco pasos; máximo permitido cuatro | 422 |
| P26 | Prompt injection | Código malicioso en AST local | 200, solo lectura |

### Ejecución local

```powershell
python scripts\pruebas_produccion.py --base-url http://127.0.0.1:8765 --output docs\evidencias\semana-4\pruebas-locales.json
```

### Ejecución pública obligatoria

```powershell
python scripts\pruebas_produccion.py --base-url https://URL-PUBLICA --output docs\evidencias\semana-4\pruebas-publicas.json
```

La evidencia pública debe contener 26/26 aprobados, el dominio HTTPS real y fecha UTC.

### Resultado local ejecutado

El 4 de noviembre de 2026 se ejecutó la matriz contra un Uvicorn temporal en
`http://127.0.0.1:8765`: **26/26 escenarios aprobados**. La evidencia está en
`docs/evidencias/semana-4/pruebas-locales.json`. Este resultado no sustituye la
ejecución contra HTTPS público.

## Prompt injection

Se prueban dos superficies:

- Código: comentarios y cadenas que solicitan ignorar reglas, revelar claves o escribir archivos.
- Documentos RAG: fragmentos que intentan convertirse en instrucciones del sistema.

Controles comprobables:

- `_construir_contenido_usuario` serializa código y contexto dentro de JSON no confiable.
- Las reglas confiables permanecen en `system_instruction`.
- Los fragmentos RAG se etiquetan como datos que pueden contener instrucciones maliciosas.
- Las citas se validan contra IDs realmente recuperados.
- El modo AST informa una política de solo lectura y no ejecuta el payload.

Regresiones: `test_entrega4_seguridad.py`, `test_llm.py`, `test_rag_abstencion.py` y P26.

## Errores y protección de información

| Condición | Respuesta pública esperada | Evidencia |
|---|---|---|
| Cuota Gemini 429 | HTTP 503, mensaje controlado | `test_servicio_controla_error_429` |
| RAG no disponible | HTTP 503 | `test_fallo_de_rag_se_convierte_en_error_503` |
| Timeout | HTTP 504 | `test_servicio_controla_timeout_real` |
| Error genérico Gemini | HTTP 502 | pruebas LLM |
| JSON de Gemini inválido | HTTP 502 | `test_servicio_controla_json_invalido` |
| Entrada inválida | HTTP 422 sin `input` ni `ctx` | `test_entrega4_seguridad.py`, P05 y P07 |
| Clave o código en logs | No debe aparecer | `test_servicio_no_registra_claves_ni_codigo_sensible` |

Las respuestas públicas no deben incluir excepciones, rutas internas, claves, código recibido ni mensajes originales del proveedor.

## Persistencia de citas

1. Ejecutar `verificar_persistencia_citas.py capturar` contra la URL pública.
2. Guardar captura de la respuesta y del volumen montado en `/data`.
3. Reiniciar el servicio o realizar un redeploy conservando el volumen.
4. Ejecutar la acción `verificar` con el mismo baseline.
5. Conservar `persistencia-antes.json`, `persistencia-despues.json` y logs del reinicio.

El comparador exige el mismo objetivo y el conjunto completo de IDs. Solo informa continuidad de citas: no certifica persistencia del volumen ni que hubo un reinicio. El arranque puede reconstruir IDs iguales. Se necesitan además el evento de reinicio, el volumen y la recuperación sin reingesta. No se dispone de acceso para reiniciar Railway y el responsable no puede hacerlo durante esta revisión.

## Auditoría de secretos

`scripts/auditar_secretos.py` revisa archivos rastreados, historial, `.env`, logs, `.dockerignore` y Dockerfile. Nunca imprime el valor encontrado. Debe complementarse con la revisión de variables ocultas en el panel de hosting.

## Criterio de aprobación

- Suites backend y frontend terminan con código 0.
- Build del frontend termina con código 0.
- Auditoría de secretos sin hallazgos.
- 26/26 escenarios locales aprobados.
- 26/26 escenarios públicos aprobados.
- Citas presentes antes y después del reinicio.

Los dos últimos puntos permanecen pendientes mientras no exista una URL pública accesible y un volumen remoto verificable.

## Resultados automatizados actuales

> Los resultados siguientes corresponden a la base previa a Ruff/Bandit. La actualización integrada, los hallazgos y bloqueos están en `docs/12-cierre-qa-entrega4.md`.

- Backend: 115 pruebas aprobadas, 0 fallidas.
- Frontend habitual: 58 aprobadas, 9 integraciones HTTP omitidas de forma intencional, 0 fallidas.
- Integración HTTP separada: 9/9 aprobadas con FastAPI y ChromaDB reales y proveedor simulado.
- ESLint: sin errores.
- Build: correcto, con advertencia no bloqueante por tamaño del chunk principal.
- Auditoría de secretos: aprobada, 0 patrones de secreto detectados.
- Sintaxis de Compose: válida.
- Contenedor y reinicio local: pendientes porque Docker Desktop Engine no estaba iniciado.
