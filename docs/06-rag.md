# Diseño e implementación de RAG

## 1. Objetivo

El sistema utiliza recuperación aumentada por generación (RAG) para proporcionar al modelo documentación relacionada con la seguridad del código Python.

El objetivo es fundamentar los hallazgos con referencias recuperadas de una base de conocimiento y permitir que el sistema se abstenga cuando no encuentra documentación de seguridad suficientemente relevante.

El código analizado se trata como información de entrada y no se ejecuta.

## 2. Fuentes de conocimiento

La documentación de seguridad se encuentra en:

- `knowledge/seguridad_python.md`

Contiene seis reglas resumidas relacionadas con:

- Uso de `eval` con entradas no confiables.
- Prevención de inyección SQL.
- Prevención de inyección de comandos del sistema.
- Prevención general de inyecciones.
- Exposición de credenciales y secretos.
- Path Traversal y acceso inseguro a archivos.

Las reglas incluyen referencias a documentación de MITRE y OWASP. El documento contiene resúmenes técnicos y enlaces a las fuentes originales, no copias completas de las páginas oficiales.

La colección adicional `contexto_proyecto` almacena fragmentos del repositorio para recuperar contexto sobre la arquitectura y la implementación del sistema.

Las colecciones utilizadas por el servicio RAG son:

- `seguridad_python`
- `contexto_proyecto`

## 3. Proceso de ingesta

El proceso de ingesta de documentación de seguridad se implementa en:

`scripts/ingest.py`

El procedimiento es el siguiente:

1. Comprueba que existe el documento de entrada.
2. Lee el archivo Markdown con codificación UTF-8.
3. Identifica las secciones delimitadas por encabezados `##`.
4. Extrae el título y el contenido de cada sección.
5. Recupera los metadatos disponibles de la fuente.
6. Genera identificadores estables para los fragmentos.
7. Inserta o actualiza los documentos y sus metadatos en ChromaDB mediante `upsert`.
8. Elimina los fragmentos obsoletos del documento procesado.
9. Ejecuta una consulta semántica para comprobar la recuperación.

La colección utiliza almacenamiento persistente en `data/chroma`.

Los identificadores se generan a partir del nombre del documento y del orden de las secciones. Esto permite actualizar los registros existentes al repetir la ingesta sin duplicar los fragmentos que conservan el mismo identificador.

### 3.1. Ingesta de documentación de seguridad

La ingesta se puede ejecutar desde la raíz del repositorio:

```powershell
python .\scripts\ingest.py
```

La ejecución verificada produjo los siguientes resultados:

- Documento procesado: `knowledge/seguridad_python.md`.
- Fragmentos procesados: 6.
- Colección: `seguridad_python`.
- Registros finales: 6.
- Fragmentos obsoletos eliminados: 1.

Los cuatro fragmentos corresponden a las cuatro reglas de seguridad documentadas.

Los resultados de recuperación incluyeron referencias a MITRE y OWASP.

### 3.2. Ingesta del contexto del proyecto

El contexto interno del repositorio se procesa mediante:

`scripts/ingest_proyecto.py`

Su ejecución se realiza desde la raíz del repositorio:

```powershell
python .\scripts\ingest_proyecto.py
```

En la sincronización realizada el 29 de octubre de 2026 se obtuvieron los siguientes resultados:

| Indicador | Resultado |
|---|---:|
| Archivos encontrados | 38 |
| Fragmentos preparados | 96 |
| Registros guardados | 96 |
| Registros finales | 96 |

Distribución de los fragmentos:

| Área | Fragmentos |
|---|---:|
| Backend | 20 |
| Documentación | 34 |
| Frontend | 28 |
| QA | 14 |
| **Total** | **96** |

La comprobación posterior confirmó que la colección `contexto_proyecto` contenía 96 registros.

La ingesta utiliza `upsert` y no elimina automáticamente los registros antiguos. Por esta razón, se debe comprobar la correspondencia entre los identificadores actuales y los existentes antes de eliminar registros obsoletos.

La sincronización debe mantener los fragmentos actuales sin eliminar información válida de otras fuentes.

## 4. Estrategia de fragmentación

La estrategia utilizada para la documentación de seguridad consiste en crear un fragmento por sección Markdown de nivel `##`.

La documentación actual produce seis fragmentos.

### 4.1. Justificación

Cada sección describe una regla de seguridad relativamente independiente.

Conservar el título y el contenido de la sección facilita recuperar la regla correspondiente y mantener el contexto documental.

El solapamiento entre secciones es cero.

El tamaño del fragmento depende de la extensión de la sección original, en lugar de utilizar una cantidad fija de caracteres.

Para el contexto interno del proyecto se utiliza un proceso de ingesta independiente, implementado en `scripts/ingest_proyecto.py`.

La ejecución registrada produjo 96 fragmentos a partir de 38 archivos del repositorio.

### 4.2. Limitaciones

Una sección excesivamente extensa puede incluir conceptos diferentes y reducir la precisión de la recuperación.

Si la documentación aumenta, será necesario evaluar una fragmentación más pequeña y comparar los resultados mediante el conjunto de evaluación.

También se debe evaluar si la estrategia utilizada para el contexto interno del proyecto necesita ajustes según el tipo de archivo.

## 5. Embeddings y almacenamiento vectorial

El motor de almacenamiento vectorial es ChromaDB.

La base de datos persistente se encuentra en:

```text
data/chroma
```

Las colecciones utilizadas son:

- `seguridad_python`
- `contexto_proyecto`

ChromaDB genera los embeddings de los documentos cuando se indexan sin proporcionar vectores explícitos y permite recuperar fragmentos mediante similitud semántica.

La colección de seguridad utiliza la distancia coseno mediante la configuración:

`hnsw:space = cosine`

Las distancias se utilizan para ordenar y filtrar los resultados recuperados.

El entorno utilizado en las comprobaciones registró ChromaDB 1.5.9.

## 6. Metadatos de las fuentes

Los fragmentos de seguridad pueden incluir los siguientes metadatos:

- `document`: archivo documental de origen.
- `section`: título de la sección.
- `category`: categoría del conocimiento.
- `source_name`: nombre de la fuente original.
- `source_section`: sección de la fuente original.
- `source_url`: enlace de referencia.
- `review_date`: fecha de revisión, cuando está disponible.
- `effective_date`: fecha de vigencia, cuando está documentada.

Los fragmentos del contexto interno también pueden incluir metadatos como:

- `source_path`: ruta del archivo original.
- `source_type`: tipo de fuente.
- `area`: área del proyecto.
- `section`: sección o título identificado.
- `chunk_index`: posición del fragmento.
- `extension`: extensión del archivo.

Los metadatos permiten identificar el origen de los fragmentos y proporcionar referencias al usuario.

La fecha de revisión no equivale a la fecha de vigencia.

En el documento `knowledge/seguridad_python.md` aparece la fecha de revisión 2026-10-28. Esta fecha corresponde a la revisión del resumen técnico y no representa una fecha de vigencia legal.

Si el documento de entrada no proporciona una fecha de vigencia, el sistema no debe inventarla.

En la ingesta verificada se procesaron seis fragmentos de seguridad y sus resultados incluyeron referencias a MITRE y OWASP.

## 7. Recuperación de información

La recuperación se implementa en:

```text
backend/app/services/rag.py
```

La función principal es:

`buscar_fragmentos(pregunta, limite=3)`

Esta función consulta las colecciones disponibles y recupera los fragmentos semánticamente relacionados con el código recibido.

### 7.1. Configuración de la recuperación

El servicio utiliza un umbral de distancia configurable mediante la variable de entorno:

`RAG_MAX_DISTANCE`

La configuración predeterminada verificada utiliza:

- Límite habitual de resultados: 3 fragmentos.
- Límite máximo permitido: 10 fragmentos.
- Distancia máxima predeterminada: `0.75`.
- Ordenación por distancia ascendente.
- Prioridad de seguridad únicamente cuando las distancias son iguales.

El límite se aplica al conjunto combinado de resultados de las colecciones consultadas.

### 7.2. Procedimiento de recuperación

El proceso realizado por `buscar_fragmentos` es el siguiente:

1. Comprueba que la pregunta no esté vacía.
2. Verifica que exista la base de datos persistente.
3. Abre una conexión con ChromaDB.
4. Consulta las colecciones `seguridad_python` y `contexto_proyecto`.
5. Recupera los documentos, metadatos y distancias.
6. Descarta los fragmentos que superan el umbral configurado.
7. Conserva los identificadores originales de ChromaDB.
8. Combina los resultados recuperados.
9. Ordena los fragmentos por distancia semántica ascendente.
10. Utiliza el tipo de fuente como criterio secundario de ordenación.
11. Aplica el límite final de resultados.
12. Devuelve los fragmentos con sus metadatos y referencias.

### 7.3. Criterio de ordenación

El servicio combina resultados de las colecciones `seguridad_python` y `contexto_proyecto`.

Los resultados se ordenan primero por distancia semántica ascendente.

Cuando dos resultados tienen la misma distancia, se priorizan los fragmentos de seguridad.

Esta estrategia permite conservar la relevancia semántica sin favorecer sistemáticamente una colección sobre otra.

Una distancia menor indica mayor similitud según la métrica utilizada.

El umbral es una heurística y debe evaluarse con ejemplos representativos del dominio.

El servicio conserva:

- Identificador del fragmento.
- Texto recuperado.
- Documento de origen.
- Sección.
- Fuente original.
- URL.
- Distancia.
- Área.
- Tipo de fuente.
- Colección.
- Fecha de revisión, cuando está disponible.

### 7.4. Limitaciones de la recuperación

La implementación actual realiza recuperación semántica.

Todavía debe evaluarse si hacen falta filtros explícitos por metadatos o una estrategia de búsqueda híbrida para términos técnicos exactos, identificadores y patrones específicos de seguridad.

También debe comprobarse que los documentos recuperados sean pertinentes para cada consulta.

La recuperación de un fragmento no significa automáticamente que ese fragmento justifique un hallazgo.

## 8. Integración con el análisis

El servicio de IA se encuentra en:

```text
backend/app/services/llm.py
```

El procedimiento de análisis es el siguiente:

1. Recibe el código Python.
2. Recupera fragmentos mediante RAG.
3. Añade las referencias recuperadas al contexto de Gemini.
4. Solicita hallazgos estructurados.
5. Valida la respuesta mediante los modelos Pydantic.
6. Comprueba que las líneas de los hallazgos existan en el código.
7. Comprueba las referencias utilizadas por los hallazgos.
8. Conserva las fuentes recuperadas para devolverlas al cliente.

Los modelos de datos utilizados se encuentran en:

```text
backend/app/models/analisis.py
```

El modelo `Hallazgo` incluye el campo:

`referencias: list[str]`

Este campo permite identificar los fragmentos exactos de ChromaDB que respaldan un hallazgo.

El modelo `Fuente` conserva el identificador del fragmento y sus metadatos.

El modelo `RespuestaAnalisis` permite devolver:

- Archivo analizado.
- Estado del análisis.
- Hallazgos.
- Fuentes.
- Mensaje de abstención, cuando corresponda.

La existencia de una fuente recuperada no demuestra por sí sola que respalde un hallazgo concreto.

Por esta razón, el servicio valida la correspondencia entre los identificadores citados y las fuentes recuperadas.

## 9. Abstención

La abstención evita presentar hallazgos como si estuvieran fundamentados cuando no se encuentran fuentes de seguridad suficientemente relevantes.

La respuesta puede incluir:

- `estado`: `abstenido`.
- `hallazgos`: una lista vacía.
- `fuentes`: una lista vacía.
- `mensaje`: explicación de la abstención.

El sistema contempla distintos escenarios de abstención:

1. No existen fuentes recuperadas.
2. El contexto documental está vacío.
3. El hallazgo no incluye referencias.
4. El hallazgo utiliza una referencia que no existe.
5. No existe evidencia suficiente para fundamentar el resultado.

La abstención se implementa en la integración del servicio RAG con el servicio LLM.

### 9.1. Pruebas de abstención

Las pruebas se encuentran en:

```text
backend/tests/test_rag_abstencion.py
```

Se verificaron los siguientes escenarios:

- Abstención cuando no existen fuentes.
- Abstención cuando el contexto está vacío.
- Abstención cuando el hallazgo no tiene referencias.
- Rechazo de referencias inventadas.
- Aceptación de hallazgos con referencias reales.
- Tratamiento de documentos maliciosos como datos.
- Rechazo de hallazgos sin citas justificadas por documentos maliciosos.

Resultado registrado:

```text
7 passed
```

Estas comprobaciones respaldan el comportamiento para los casos probados, pero no garantizan que todas las consultas sin respuesta documental se identifiquen correctamente.

Es necesario ampliar la evaluación y registrar los falsos positivos y negativos.

## 10. Seguridad frente a instrucciones maliciosas

Los documentos recuperados deben tratarse como datos de referencia y no como instrucciones para el modelo.

El servicio añade instrucciones para que Gemini no obedezca órdenes incluidas en los fragmentos documentales.

También indica que el contenido recuperado debe utilizarse únicamente cuando sea pertinente para fundamentar el análisis.

Esta medida reduce el riesgo de que una instrucción maliciosa indexada altere el comportamiento del análisis.

Las pruebas automatizadas incluyen documentos que contienen instrucciones maliciosas y comprueban que:

- El contenido documental se trata como información no confiable.
- Las instrucciones encontradas dentro de los documentos no deben sustituir las instrucciones del sistema.
- Un documento malicioso no justifica un hallazgo sin una referencia válida.

Estas pruebas respaldan los escenarios comprobados, pero no constituyen una garantía absoluta frente a todos los ataques de inyección de instrucciones.

## 11. Pruebas y evidencias

### 11.1. Pruebas automatizadas del servicio LLM

Las pruebas se encuentran en:

```text
backend/tests/test_llm.py
```

Se comprobaron los siguientes escenarios:

- Respuesta JSON válida.
- Respuesta vacía del proveedor.
- Error 429.
- Timeout 504.
- JSON inválido.
- Timeout real.
- Protección de claves API en mensajes de error.
- Rechazo de líneas inexistentes.
- Tratamiento del código malicioso como datos.
- Protección de información sensible en los registros.

Resultado registrado:

```text
10 passed
```

### 11.2. Pruebas de abstención RAG

Se ejecutaron las pruebas de:

```text
backend/tests/test_rag_abstencion.py
```

Resultado registrado:

```text
7 passed
```

### 11.3. Pruebas combinadas

Se ejecutaron los dos archivos de pruebas desde la carpeta `backend`:

```powershell
python -m pytest .\tests\test_llm.py .\tests\test_rag_abstencion.py -q
```

Resultado registrado:

```text
17 passed
```

### 11.4. Suite completa del backend

También se ejecutó la suite completa:

```powershell
python -m pytest -q
```

Resultado registrado:

```text
51 passed
```

La suite completa aprobó las 51 pruebas existentes en esa ejecución.

Este resultado corresponde a la ejecución general registrada y no sustituye la necesidad de añadir pruebas específicas para la recuperación real de ChromaDB.

### 11.5. Comprobación de sintaxis y cambios

Se ejecutó:

```powershell
python -m py_compile .\backend\app\services\rag.py
```

La compilación finalizó correctamente.

También se ejecutó:

```powershell
git diff --check
```

No se reportaron errores de espacios o formato. Git mostró advertencias relacionadas con la conversión de finales de línea LF y CRLF.

### 11.6. Evidencias técnicas

Las evidencias de la Semana 3 se almacenan en:

```text
docs/evidencias/semana-3/
```

Los archivos registrados son:

- `comparacion-ingesta.txt`
- `evaluacion-rag.txt`
- `pruebas-llm-abstencion.txt`

Estas evidencias contienen resultados de ingesta, recuperación, métricas y pruebas automatizadas.

La evidencia de comparación de ingesta debe mantenerse actualizada con la última sincronización de 96 fragmentos.

La evidencia de pruebas también debe incorporar el resultado de la suite completa de 51 pruebas.

## 12. Evaluación inicial de la recuperación RAG

### 12.1. Metodología

Se ejecutó:

```text
scripts/evaluate_rag.py
```

El evaluador realizó cuatro consultas de referencia:

1. Uso inseguro de `eval`.
2. Inyección SQL.
3. Inyección de comandos.
4. Prevención general de inyecciones.

El evaluador compara los identificadores recuperados con las referencias consideradas relevantes para cada consulta.

Se calcularon las siguientes métricas:

- Precision@3.
- Recall@3.
- MRR.
- Cobertura.

### 12.2. Resultados registrados

Los resultados de la ejecución preliminar fueron:

| Consulta | Precision@3 | Recall@3 | MRR |
|---|---:|---:|---:|
| Uso inseguro de eval | 0.333 | 1.000 | 1.000 |
| Inyección SQL | 0.667 | 1.000 | 1.000 |
| Inyección de comandos | 0.667 | 1.000 | 1.000 |
| Prevención general de inyecciones | 1.000 | 1.000 | 1.000 |
| **Promedio** | **0.667** | **1.000** | **1.000** |

Cobertura registrada: 100 %.

### 12.3. Interpretación

En las cuatro consultas evaluadas, la precisión media de los tres primeros resultados fue de 66.7 %.

El recall medio fue de 100 % y el MRR medio fue de 100 %.

El caso de inyección de comandos recuperó la regla de seguridad correspondiente en la primera posición después del cambio de ordenación.

Los resultados indican que el sistema recuperó las referencias relevantes definidas para las cuatro consultas dentro de los resultados evaluados.

### 12.4. Limitaciones de la evaluación

Estos resultados son preliminares.

El conjunto contiene únicamente cuatro consultas y las métricas dependen de las etiquetas de relevancia definidas para ellas.

No representan todavía la evaluación oficial de veinte preguntas ni demuestran la calidad de todas las respuestas generadas por Gemini.

Además, los resultados registrados corresponden a una ejecución anterior a la última sincronización de la colección `contexto_proyecto`.

Por tanto, se debe volver a ejecutar el evaluador sobre la versión definitiva de la base vectorial y de la recuperación.

Durante la ejecución registrada también apareció una advertencia:

```text
SyntaxWarning: invalid escape sequence '\S'
```

La advertencia no impidió que el evaluador terminara, pero debe corregirse en el código de `scripts/evaluate_rag.py`.

## 13. Trabajo pendiente

Antes de considerar terminado el RAG, se debe completar lo siguiente:

### 13.1. Recuperación

- Añadir o completar pruebas específicas de `buscar_fragmentos`.
- Comprobar la ordenación de los resultados.
- Verificar el límite combinado de resultados.
- Evaluar el umbral de distancia con consultas representativas.
- Comprobar la recuperación de información de ambas colecciones.
- Evaluar filtros por metadatos y búsqueda híbrida cuando proceda.
- Verificar la reproducibilidad de todas las colecciones.

### 13.2. Fundamentación y citas

- Verificar que cada referencia respalde semánticamente el hallazgo correspondiente.
- Comprobar que los identificadores devueltos por el backend sean los mismos que aparecen en las fuentes recuperadas.
- Completar la presentación de las referencias individuales en la interfaz.

### 13.3. Abstención y seguridad

- Ampliar las pruebas de abstención.
- Registrar los falsos positivos y negativos.
- Probar la resistencia a instrucciones maliciosas en documentos.
- Comprobar que el modelo no genere hallazgos sin evidencia suficiente.

### 13.4. Evaluación

- Volver a ejecutar `scripts/evaluate_rag.py` después de la sincronización definitiva.
- Corregir la advertencia de sintaxis del evaluador.
- Completar el conjunto oficial de veinte preguntas de referencia.
- Validar manualmente las referencias relevantes.
- Registrar los resultados y errores encontrados en `docs/07-evaluacion.md`.

### 13.5. Integración final

- Actualizar las evidencias técnicas de la Semana 3.
- Ejecutar nuevamente la suite completa de pruebas.
- Coordinar la integración con el agente y el frontend sin sobrescribir el trabajo de los demás.
- Verificar que las respuestas estén fundamentadas y que la abstención funcione correctamente.

## 14. Estado de la implementación

La implementación cuenta con:

- Dos colecciones persistentes en ChromaDB.
- Ingesta de documentación de seguridad.
- Ingesta del contexto interno del proyecto.
- Recuperación semántica.
- Metadatos y referencias documentales.
- Integración con Gemini.
- Validación estructurada mediante Pydantic.
- Validación de identificadores de referencias.
- Abstención ante los escenarios probados.
- Pruebas automatizadas de LLM y abstención.
- Evidencias técnicas de la Semana 3.
- Evaluación preliminar de recuperación.

La implementación ha superado las pruebas automatizadas registradas, con 51 pruebas aprobadas en la suite completa del backend.

Sin embargo, la validación definitiva del RAG requiere completar las pruebas específicas de recuperación, actualizar las evidencias después de la última sincronización, verificar la correspondencia semántica entre hallazgos y citas y completar la evaluación oficial de veinte preguntas.

El sistema se considerará validado cuando las pruebas y el conjunto de evaluación proporcionen evidencia suficiente de la recuperación, la fundamentación de las citas y la abstención ante consultas sin respaldo documental.