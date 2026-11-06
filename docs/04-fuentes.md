# 04. Inventario de fuentes documentales

Responsable documental: Ronald Yépez. Inventario consolidado el 5 de noviembre de
2026 sobre `65675e2`. Enlaces consultados en sus sitios oficiales en esta revisión.
No se presenta este inventario como evidencia original de Semana 1.

## Fuentes oficiales y correspondencia con RAG

Todas las fuentes de la tabla son páginas HTML. Se ingieren resúmenes Markdown
curados, no el contenido completo de las páginas. La fecha `2026-10-28` declarada
en el resumen es de revisión técnica; no es fecha de publicación ni vigencia legal.
No se ha definido una fecha de caducidad de estas referencias técnicas.

| ID del fragmento | Documento y origen oficial | URL | Contenido utilizado / fragmentación |
|---|---|---|---|
| `seguridad_python-001` | CWE-94, MITRE CWE | [Code Injection](https://cwe.mitre.org/data/definitions/94.html) | Riesgo de evaluación dinámica; una sección `## Regla 1` |
| `seguridad_python-002` | SQL Injection Prevention, OWASP | [Guía SQL](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) | Parametrización y validación de opciones; una sección `## Regla 2` |
| `seguridad_python-003` | OS Command Injection Defense, OWASP | [Guía comandos](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) | Argumentos y uso del intérprete; sección `## Regla 3`, incluida su ampliación `###` |
| `seguridad_python-004` | Injection Prevention, OWASP | [Guía inyecciones](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html) | Separación entre instrucciones y datos; una sección `## Regla 4` |
| `seguridad_python-005` | CWE-798, MITRE CWE | [Credenciales incrustadas](https://cwe.mitre.org/data/definitions/798.html) | Fuente principal de `## Regla 5` |
| `seguridad_python-005` | Secrets Management, OWASP | [Gestión de secretos](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) | Referencia complementaria en la misma sección; no crea otro ID |
| `seguridad_python-006` | CWE-22, MITRE CWE | [Limitación de rutas](https://cwe.mitre.org/data/definitions/22.html) | Fuente principal de `## Regla 6` |
| `seguridad_python-006` | Path Traversal, OWASP | [Página de origen](https://owasp.org/www-community/attacks/Path_Traversal) | Complemento de la misma sección; el enlace redirige al sitio Community de OWASP |

Material curado: [knowledge/seguridad_python.md](../knowledge/seguridad_python.md).
Registro de materia prima: ocho copias HTML oficiales en
[data/raw/](../data/raw/README.md), con origen, fecha y hashes en el
[manifiesto](../data/raw/fuentes.json). Las ocho páginas sustentan seis fragmentos;
las copias completas no se almacenan en ChromaDB ni se ingieren automáticamente.

## Fragmentación y metadatos efectivos

[scripts/ingest.py](../scripts/ingest.py) divide el Markdown por encabezados `##`,
normaliza saltos de línea y elimina del cuerpo las líneas de metadatos. Los
encabezados `###` permanecen dentro de la regla. No usa una ventana fija de tokens
ni solapamiento entre reglas.

Cada fragmento conserva documento, sección, categoría, fuente, URL y fecha de
revisión cuando existen. `effective_date` solo se incorpora si la fuente lo
declara. En reglas con dos fuentes, el extractor toma la primera URL como
metadato principal; el inventario conserva también el enlace complementario.

Los IDs dependen del orden de las secciones. Si se reordena el archivo, se debe
revisar el dataset y regenerar/comprobar las citas. El inventario no modifica el
corpus, los embeddings ni el índice desplegado.

## Actualización y límites

Antes de ampliar el corpus, el equipo debe verificar origen y pertinencia,
redactar el resumen, registrar revisión, ejecutar ingesta local y repetir los
casos de recuperación. No copiar documentos privados ni instrucciones ajenas
como si fueran reglas del sistema.

La colección `contexto_proyecto` contiene material del propio repositorio y es
complementaria. No reemplaza las fuentes de seguridad ni convierte todos los
patrones Ruff/Bandit en hallazgos respaldados por MITRE/OWASP.

Referencia académica para el inventario y las entregas:
[portal del seminario](https://fabig76.github.io/entregas-ia-uniandes/).
