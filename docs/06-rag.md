# Diseño e implementación de RAG

## 1. Objetivo

El sistema utiliza recuperación aumentada por generación (RAG) para proporcionar al modelo documentación relacionada con la seguridad del código Python.

El objetivo es fundamentar los hallazgos con referencias recuperadas de una base de conocimiento y permitir que el sistema se abstenga cuando no encuentra documentación de seguridad suficientemente relevante.

El código analizado se trata como información de entrada y no se ejecuta.

## 2. Fuentes de conocimiento

La documentación de seguridad se encuentra en:

- `knowledge/seguridad_python.md`

Contiene cuatro reglas resumidas relacionadas con:

- Uso de `eval` con entradas no confiables.
- Prevención de inyección SQL.
- Prevención de inyección de comandos del sistema.
- Prevención general de inyecciones.

Las reglas incluyen referencias a documentación de MITRE y OWASP. El documento contiene resúmenes técnicos y enlaces a las fuentes originales, no copias completas de las páginas oficiales.

La colección adicional `contexto_proyecto` almacena fragmentos del repositorio para recuperar contexto sobre la arquitectura y la implementación del sistema.

Las colecciones utilizadas por el servicio RAG son:

- `seguridad_python`
- `contexto_proyecto`

## 3. Proceso de ingesta

El proceso de ingesta de documentación de seguridad se implementa en `scripts/ingest.py`.

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

La ingesta se puede ejecutar desde la raíz del repositorio:

```powershell
& ".\.venv\Scripts\python.exe" ".\scripts\ingest.py"
```

## 4. Estrategia de fragmentación

La estrategia consiste en crear un fragmento por sección Markdown de nivel `##`.

La documentación actual produce cuatro fragmentos.

### Justificación

Cada sección describe una regla de seguridad relativamente independiente. Conservar el título y el contenido de la sección facilita recuperar la regla correspondiente y mantener el contexto documental.

El solapamiento entre secciones es cero.

El tamaño del fragmento depende de la extensión de la sección original, en lugar de utilizar una cantidad fija de caracteres.

### Limitaciones

Una sección excesivamente extensa puede incluir conceptos diferentes y reducir la precisión de la recuperación.

Si la documentación aumenta, será necesario evaluar una fragmentación más pequeña y comparar los resultados mediante el conjunto de evaluación.

## 5. Embeddings y almacenamiento vectorial

El motor de almacenamiento vectorial es ChromaDB.

La base de datos persistente se encuentra en:

```text
data/chroma
```

La colección de seguridad se denomina `seguridad_python`.

ChromaDB genera los embeddings de los documentos cuando se indexan sin proporcionar vectores explícitos y permite recuperar fragmentos mediante similitud semántica.

La colección utiliza la distancia coseno mediante la configuración `hnsw:space = cosine`.

Las distancias se utilizan para ordenar y filtrar los resultados recuperados.

## 6. Metadatos de las fuentes

Los fragmentos pueden incluir los siguientes metadatos:

- `document`: archivo documental de origen.
- `section`: título de la sección.
- `category`: categoría del conocimiento.
- `source_name`: nombre de la fuente original.
- `source_section`: sección de la fuente original.
- `source_url`: enlace de referencia.
- `review_date`: fecha de revisión, cuando está disponible.
- `effective_date`: fecha de vigencia, cuando está documentada.

Los metadatos permiten identificar el origen de los fragmentos y proporcionar referencias al usuario.

La fecha de revisión no equivale a la fecha de vigencia. Si el documento de entrada no proporciona una fecha de vigencia, el sistema no debe inventarla.

En la ingesta verificada se procesaron cuatro fragmentos. Los resultados de la consulta de prueba incluyeron referencias a MITRE y OWASP.

En esa ejecución no se encontró una fecha de vigencia documentada para las fuentes recuperadas.

## 7. Recuperación de información

La recuperación se implementa en:

```text
backend/app/services/rag.py
```

La función `buscar_fragmentos` consulta las colecciones disponibles y recupera los fragmentos semánticamente relacionados con el código recibido.

El servicio utiliza un límite de resultados por colección y un umbral de distancia configurado en el código.

La configuración verificada utiliza:

- Límite habitual: tres fragmentos por colección.
- Límite máximo configurable: diez fragmentos por colección.
- Distancia máxima: `0.75`.
- Ordenación de los resultados por distancia ascendente.

Una distancia menor indica mayor similitud según la métrica utilizada. El umbral es una heurística y debe evaluarse con ejemplos representativos del dominio.

El servicio conserva los identificadores, el texto, los metadatos, las URL y las distancias de los fragmentos recuperados.

### Limitaciones de la recuperación

La implementación actual realiza recuperación semántica.

Todavía debe evaluarse si hacen falta filtros explícitos por metadatos o una estrategia de búsqueda híbrida para términos técnicos exactos, identificadores y patrones específicos de seguridad.

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
7. Conserva las fuentes recuperadas para devolverlas al cliente.

Los hallazgos pueden incluir identificadores de fragmentos en el campo `referencias`. La respuesta de la API incluye las fuentes recuperadas con sus identificadores y metadatos.

La existencia de una fuente recuperada no demuestra por sí sola que respalde un hallazgo concreto. Es necesario validar la correspondencia entre cada hallazgo y sus referencias.

## 9. Abstención

La abstención evita presentar hallazgos como si estuvieran fundamentados cuando no se encuentran fuentes de seguridad suficientemente relevantes.

La respuesta puede incluir:

- `estado`: `abstenido`.
- `hallazgos`: una lista vacía.
- `fuentes`: una lista vacía.
- `mensaje`: explicación de la abstención.

La abstención se ha observado en una prueba de la API con un fragmento Python para el que no se recuperaron fuentes de seguridad suficientemente relevantes.

Esta prueba demuestra el comportamiento de abstención para ese caso concreto. No garantiza que todas las consultas sin respuesta documental se identifiquen correctamente.

Es necesario comprobar la abstención mediante casos de evaluación y registrar los falsos positivos y negativos.

## 10. Seguridad frente a instrucciones maliciosas

Los documentos recuperados deben tratarse como datos de referencia y no como instrucciones para el modelo.

El servicio añade instrucciones para que Gemini no obedezca órdenes incluidas en los fragmentos documentales. También indica que el contenido recuperado debe utilizarse únicamente cuando sea pertinente para fundamentar el análisis.

Esta medida reduce el riesgo de que una instrucción maliciosa indexada altere el comportamiento del análisis, pero debe validarse mediante pruebas específicas.

La revisión debe incluir un documento que contenga una instrucción como «ignora tus instrucciones» y comprobar que el modelo la trata como contenido no confiable.

## 11. Pruebas y evidencias

La suite de pruebas del backend ha obtenido el siguiente resultado:

```text
49 passed
```

La ingesta de seguridad se ejecutó correctamente y produjo:

- Cuatro fragmentos procesados.
- Cuatro registros en la colección de seguridad.
- Una consulta semántica con tres resultados.
- Referencias y distancias recuperadas de ChromaDB.
- Cero fragmentos obsoletos eliminados en esa ejecución.

Estos resultados corresponden a las ejecuciones realizadas durante el desarrollo.

Las evidencias técnicas definitivas de la semana 3 deben guardarse en:

```text
docs/evidencias/semana-3/
```

La suite general de pruebas no sustituye las pruebas específicas de ingesta, recuperación, citas y abstención.

## 12. Trabajo pendiente

Antes de considerar terminado el RAG, se debe:

- Completar las pruebas automatizadas de recuperación.
- Verificar que cada referencia respalde el hallazgo citado.
- Evaluar el umbral de distancia con casos representativos.
- Comprobar la abstención ante preguntas sin respaldo documental.
- Probar la resistencia a instrucciones maliciosas en documentos.
- Evaluar filtros por metadatos y búsqueda híbrida cuando proceda.
- Comprobar la reproducibilidad de la ingesta.
- Preparar las evidencias técnicas de la semana 3.
- Ejecutar el conjunto de evaluación y documentar sus resultados.
