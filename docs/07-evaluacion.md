# 07. Evaluación — semana 3

**Responsable:** Compañero 2, Frontend y Evaluación.  
**Fecha:** 30 de octubre de 2026, America/Bogota.  
**Rama de trabajo:** `feature/frontend`, actualizada con `origin/main`.  
**Revisión base:** `8f27ddc9971f328ae122e6c71e50726ef898c1f0`.

## 1. Alcance y estado de la entrega

Se revisó y mejoró la presentación de fuentes del backend. Se prepararon 20 preguntas con código y respuestas de referencia, un ejecutor reproducible y evidencias de pruebas, recuperación real y revisión visual.

**La recuperación RAG se evaluó realmente en 20 casos. La calidad de las respuestas de Gemini queda pendiente:** el backend local responde HTTP 503 porque `GEMINI_API_KEY` no está configurada. No se atribuyen a la IA resultados de pruebas simuladas, ni se reutilizan como actuales las evidencias de semanas anteriores.

## 2. Fuentes en la interfaz

El contrato actual devuelve `fuentes[]` con `id`, `documento`, `seccion`, `fuente`, `url` y `distancia`. Cada hallazgo devuelve `referencias[]` con IDs exactos. La asociación se realiza por ID dentro del informe de cada archivo, antes de reunir los informes ZIP.

Cambios implementados:

- Tarjetas con título, sección, ID y enlace separados; texto largo ajustable al ancho de pantalla.
- «Referencias citadas en este hallazgo» separadas de «Fuentes de conocimiento consultadas». Recuperar un documento no demuestra que sustente todos los hallazgos.
- Enlaces absolutos HTTP/HTTPS sin credenciales; el resto muestra «Enlace no disponible». Los enlaces abren otra pestaña con `noopener noreferrer` y nombre accesible.
- Texto del servidor renderizado como texto de React. No se inserta HTML del backend.
- Aviso para referencias cuyos metadatos no fueron recibidos; nunca se inventan fuentes.
- Fuentes idénticas deduplicadas en un informe; IDs con metadatos contradictorios rechazados.
- Una cita de un archivo ZIP no se resuelve usando una fuente recibida exclusivamente en otro archivo.
- Abstención y observaciones de análisis parcial visibles. Exportación JSON conserva `estado` y `mensaje`, además de fuentes y hallazgos.
- Durante una nueva carga se oculta la lista general de fuentes del resultado anterior.

La distancia de recuperación no se muestra como porcentaje de confianza: es una distancia semántica, no una probabilidad de corrección.

## 3. Conjunto de referencia

Archivo: [`eval/preguntas_referencia.json`](../eval/preguntas_referencia.json). Se validaron 20 IDs únicos, campos, sintaxis Python, expresiones de coincidencia y líneas esperadas, sin ejecutar los fragmentos.

| Grupo | Casos | Hallazgos esperados | Controles negativos |
|---|---|---:|---:|
| Inyección SQL | P01–P06 | 4 | 2 |
| Inyección de comandos | P07–P12 | 4 | 2 |
| Ejecución dinámica | P13–P18 | 4 | 2 |
| Fuera de cobertura documental | P19–P20 | 0 | 2 abstenciones esperadas |

Las preguntas explican el propósito; se envía el código al endpoint `/api/v1/analizar`, que no recibe una pregunta en lenguaje natural. Las respuestas de referencia y los IDs esperados derivan de las cuatro reglas existentes en `knowledge/seguridad_python.md`:

| ID | Fuente documental |
|---|---|
| `seguridad_python-001` | [MITRE CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| `seguridad_python-002` | [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) |
| `seguridad_python-003` | [OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) |
| `seguridad_python-004` | [OWASP Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html) |

Son etiquetas propuestas para revisión del equipo. No constituyen una evaluación independiente ni cubren todas las vulnerabilidades Python. Los controles seguros también tienen documentos relevantes para valorar sus mecanismos de prevención; recuperarlos no equivale a producir un falso positivo.

## 4. Método y métricas

### Recuperación

Se llamó al flujo real `_construir_consulta_rag` → `_recuperar_contexto_rag`, con ChromaDB 1.5.9, colección local `seguridad_python`, cuatro fragmentos, distancia máxima 0,75 y embeddings predeterminados `all-MiniLM-L6-v2`. No se ingirió `contexto_proyecto` en esta ejecución. Las métricas miden las fuentes de seguridad devueltas y conservan su orden; los IDs repetidos cuentan una sola vez.

- **Precision@3:** IDs relevantes recuperados entre los tres primeros, divididos por 3, incluso si se devuelven menos resultados.
- **Recall@3:** IDs relevantes recuperados entre los tres primeros, divididos por los IDs esperados del caso.
- **MRR@3:** inverso de la posición del primer ID relevante; cero si no aparece en los tres primeros.
- **Hit@3:** proporción de casos con al menos un ID relevante entre los tres primeros.
- Los promedios anteriores incluyen los **18 casos con referencias esperadas**. P19 y P20 se evalúan por ausencia de fuentes y no se agregan artificialmente como recall perfecto.
- Se informa completitud, errores y latencia por separado. La consulta de calentamiento está fuera de la medición; cada caso incluye transformación, recuperación y procesamiento local, no generación de IA.

### Respuestas de la API

El ejecutor también está preparado para calcular precisión, recall y F1 de hallazgos, exactitud por caso, abstención, líneas fuera de rango, cobertura de citas y proporción de referencias resueltas. El emparejamiento de hallazgos es uno a uno, por patrón de categoría/título y una línea etiquetada como admisible.

`precisión = TP / (TP + FP)`; `recall = TP / (TP + FN)`; `F1 = 2TP / (2TP + FP + FN)`. Los cocientes sin denominador se guardan como `null`. Los errores de ejecución quedan fuera de esos denominadores y se exponen en completitud y aciertos sobre el total; no se cuentan como respuestas correctas. Las abstenciones ante casos que requerían análisis tampoco son aciertos.

La resolución de IDs verifica trazabilidad estructural. No mide veracidad de la explicación, pertinencia de la fuente, corrección de la solución ni calibración de severidad; estos aspectos requieren revisión humana de las respuestas reales.

## 5. Resultados obtenidos

### Recuperación real, sin proveedor de IA

Evidencia: [`rag-20-casos/resultados.json`](evidencias/semana-3/rag-20-casos/resultados.json), [CSV](evidencias/semana-3/rag-20-casos/resultados.csv) y [resumen automático](evidencias/semana-3/rag-20-casos/resumen.md).

| Métrica | Resultado | Denominador |
|---|---:|---|
| Completitud | 100 % | 20/20 casos |
| Errores de ejecución | 0 | 20 casos |
| Precision@3 media | 53,70 % | 18 casos con etiquetas |
| Recall@3 medio | 94,44 % | 18 casos con etiquetas |
| MRR@3 medio | 88,89 % | 18 casos con etiquetas |
| Hit@3 | 94,44 % | 17/18 casos |
| Ausencia de fuentes fuera de cobertura | 100 % | 2/2 casos |
| Latencia media | 320,20 ms | 20 casos, tras calentamiento |
| Latencia p95 | 339,21 ms | rango más próximo, 20 casos |

**Interpretación:** los casos tienen uno o dos documentos relevantes etiquetados. Con el denominador fijo 3, la Precision@3 máxima de este conjunto sería 55,56 %; el 53,70 % observado no debe interpretarse como exactitud del sistema. La muestra de dos casos fuera de cobertura es insuficiente para generalizar la capacidad de abstención.

P18 («Operaciones fijas») no recuperó referencias. El fragmento selecciona una función de `operator` desde un mapa permitido; la consulta transformada conserva ese código y no recupera la regla esperada de ejecución dinámica bajo el umbral actual. Es una discrepancia de recuperación/etiquetado en un control negativo, **no una vulnerabilidad omitida demostrada**. Conviene revisar primero si esa regla debe ser relevante para este caso y luego valorar cambios de consulta o cobertura documental.

### API local

El servidor se inició en `http://127.0.0.1:8000`. Se enviaron los 20 casos al endpoint real: **20 respuestas HTTP 503, 0 análisis completados**. La causa observada es «Proveedor de IA no configurado»; falta `GEMINI_API_KEY`. La comprobación `/health` solo acredita que la API está levantada.

Evidencia: [`api-sin-configurar/resultados.json`](evidencias/semana-3/api-sin-configurar/resultados.json) y [diagnóstico de la API](evidencias/semana-3/api-diagnostico.json). Precisión, recall, F1, latencia de respuestas válidas, citas y abstención de IA quedan **no disponibles**, no aprobadas ni estimadas a partir de mocks.

### Pruebas y presentación

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Frontend, Vitest | 52 aprobadas | [Registro](evidencias/semana-3/frontend-pruebas.txt) |
| Backend, pytest existente | 58 aprobadas | [Registro](evidencias/semana-3/backend-pruebas.txt) |
| Evaluador, unittest | 10 aprobadas | [Registro](evidencias/semana-3/evaluador-pruebas.txt) |
| Dataset | 20 casos válidos | [Registro](evidencias/semana-3/dataset-validacion.txt) |
| ESLint | Sin errores | [Registro](evidencias/semana-3/frontend-lint.txt) |
| Compilación de producción | Correcta; advertencia de tamaño | [Registro](evidencias/semana-3/frontend-build.txt) |
| Escritorio y móvil | Fuentes legibles; ancho de documento 390 px para viewport 390 px | [Escritorio](evidencias/semana-3/01-fuentes-escritorio.jpg), [móvil](evidencias/semana-3/02-fuentes-movil.jpg) |
| Abstención y metadatos faltantes | Mensajes explícitos | [Abstención](evidencias/semana-3/03-abstencion-movil.jpg), [referencia ausente](evidencias/semana-3/04-referencia-ausente.jpg) |
| ZIP parcial | Advertencia visible | [Captura](evidencias/semana-3/05-zip-parcial.jpg) |

Las pruebas unitarias usan respuestas y proveedores simulados según la suite; no sustituyen una prueba completa con Gemini. Las capturas nuevas corresponden al componente real con datos simulados, identificados en la propia página. La [captura original del usuario](evidencias/semana-3/00-captura-original-usuario.png) se conserva como evidencia del problema inicial, no como ejecución propia.

## 6. Errores y limitaciones encontradas

| ID | Hallazgo | Tratamiento / estado |
|---|---|---|
| FE-01 | Fuentes sin estilos: título, sección, ID y enlace concatenados visualmente | Corregido con componente y tarjetas compartidas |
| FE-02 | Unión global de fuentes ZIP podía atribuir a un archivo fuentes recibidas solo en otro | Corregido resolviendo citas dentro de cada informe; prueba de regresión |
| FE-03 | Exportación JSON omitía estado y mensaje de abstención | Corregido; conserva también observaciones parciales |
| FE-04 | El panel no mostraba el mensaje de abstención parcial de ZIP | Corregido con aviso visible |
| FE-05 | URLs apenas comprobadas por prefijo y fuentes duplicadas | Validación de URL y metadatos; deduplicación y pruebas |
| EV-01 | P18 no recupera la referencia etiquetada | Pendiente revisar etiqueta y cobertura; no ajustar el conjunto para mejorar una cifra |
| EV-02 | Proveedor de IA sin configurar; HTTP 503 en 20 casos | Pendiente que responsable de backend configure la clave local y repetir modo API |
| EV-03 | Evidencia heredada `evaluacion-rag.txt` corresponde a otro conjunto y muestra documentos históricos recuperados | Conservada sin cambios; separada de esta ejecución con hashes y fecha |
| EV-04 | Paquete de Monaco supera la recomendación de 500 kB | Advertencia de compilación; pendiente optimización de carga, fuera del cambio de fuentes |

No se modificó la lógica del backend ni se ajustaron umbrales para mejorar resultados. No hay una medición con usuarios, auditoría integral de accesibilidad ni validación semántica automática de citas.

## 7. Reproducción y siguiente paso

La guía completa de comandos está en [`eval/README.md`](../eval/README.md). Los resultados guardan versiones, hashes del dataset/evaluador/conocimiento/servicios y revisión base; se indica que había cambios locales. El entorno Python exacto está en [entorno-python.txt](evidencias/semana-3/entorno-python.txt).

Para completar la evaluación de respuestas, el responsable de backend debe configurar el `.env` local, reiniciar la API y ejecutar desde la raíz:

```powershell
.\.venv\Scripts\python.exe eval/run_eval.py --mode api --base-url http://127.0.0.1:8000
```

Se debe revisar cada respuesta respecto a `respuesta_referencia`, validar la pertinencia de las citas y la corrección sugerida, y agregar el nuevo resultado al informe conservando la evidencia del bloqueo inicial. Hasta entonces, la entrega acredita funcionamiento del frontend, pruebas del software y recuperación RAG; **no acredita calidad de respuestas completas de IA**.

## 8. Integración posterior del diseño aprobado

Se implementó la propuesta visual v3 elegida por el usuario, con paleta azul noche, turquesa y ámbar, encabezado académico, editor e informe en dos paneles y una sección de trazabilidad del hallazgo seleccionado. El ejemplo inicial pasó a ser `usuarios.py` con nueve líneas y un hallazgo SQL ilustrativo en la línea 6. Los tres patrones originales siguen disponibles en el servicio de demostración y sus pruebas.

La nueva suite del frontend tiene **58 pruebas aprobadas**. Las fuentes de Demo se identifican como referencias ilustrativas sin recuperación RAG; el modo API mantiene la asociación por archivo y los estados de abstención y análisis parcial. Se verificaron en navegador los filtros, la ubicación de líneas, la descarga JSON, la carga de Python, la cancelación, el estado vacío y el error HTTP 503 del backend local. El bloqueo de evaluación con Gemini sigue vigente.

Las [evidencias del rediseño](evidencias/semana-3/redisenointerfaz/README.md) se guardan aparte de la corrida original de recuperación y sus métricas. Las capturas nuevas corresponden a la aplicación React integrada, con viewport de escritorio y móvil.
