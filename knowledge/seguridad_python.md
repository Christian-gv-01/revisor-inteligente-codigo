# Base de conocimiento de seguridad Python



Documento: seguridad_python.md

Fecha de revision: 2026-10-28

Tipo: resumen tecnico con referencias oficiales.

Nota de vigencia: la fecha es la de revision del resumen, no una fecha de vigencia legal.



## Regla 1: Evitar eval con entradas no confiables



Documento fuente: MITRE CWE-94

Seccion: Code Injection y recomendaciones para Python

URL fuente: https://cwe.mitre.org/data/definitions/94.html

Fecha de revision: 2026-10-28



La funcion eval puede ejecutar expresiones construidas a partir de datos externos. Si una persona puede controlar la entrada evaluada, puede provocar ejecucion de codigo no prevista.



Durante la revision, comprobar si eval recibe datos controlados por el usuario. Recomendar alternativas que no ejecuten codigo arbitrario.



ast.literal_eval limita la evaluacion a literales, pero tampoco debe considerarse una solucion universal para entradas no confiables, porque entradas profundamente anidadas pueden consumir demasiados recursos.



## Regla 2: Prevenir inyeccion SQL



Documento fuente: OWASP SQL Injection Prevention Cheat Sheet

Seccion: Primary Defenses y Allow-List Input Validation

URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

Fecha de revision: 2026-10-28



Las consultas SQL no deben construirse concatenando datos no confiables dentro de la instruccion SQL.



Preferir consultas parametrizadas o sentencias preparadas para separar la estructura de la consulta de sus valores.



Si el usuario puede elegir nombres de columnas, tablas u ordenamientos, usar opciones fijas permitidas por la aplicacion. Validar una entrada no sustituye la parametrizacion de la consulta.



## Regla 3: Prevenir inyeccion de comandos del sistema



Documento fuente: OWASP OS Command Injection Defense Cheat Sheet

Seccion: Defensas contra la inyeccion de comandos

URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html

Fecha de revision: 2026-10-28



Existe riesgo cuando datos controlados externamente modifican el comando del sistema que ejecuta la aplicacion.



Preferir APIs que no invoquen un interprete de comandos. No concatenar entradas no confiables en comandos. Si una operacion del sistema es necesaria, limitar las opciones permitidas y aplicar el principio de minimo privilegio.



Durante la revision, buscar usos de funciones de ejecucion de comandos y comprobar de donde proceden sus argumentos.



### Ampliacion de la Regla 3: subprocess y shell=True



Patrones de revision:



- subprocess.run()

- subprocess.call()

- subprocess.Popen()

- subprocess.check_output()

- os.system()

- os.popen()

- shell=True



Existe riesgo de inyeccion de comandos cuando argumentos controlados por usuarios o fuentes externas llegan a un interprete de comandos sin proteccion adecuada.



Revisar especialmente llamadas como:



```python

subprocess.run(comando, shell=True)

os.system(comando)

subprocess.Popen(comando, shell=True)

```



Preferir subprocess con una lista de argumentos y shell=False.



Utilizar ejecutables permitidos, validar los argumentos y evitar que datos externos puedan modificar la operacion.



No clasificar automaticamente cualquier llamada a subprocess como vulnerable. Comprobar el origen y el tratamiento de los argumentos.



## Regla 4: Prevencion general de inyecciones



Documento fuente: OWASP Injection Prevention Cheat Sheet

Seccion: Injection Prevention Rules

URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html

Fecha de revision: 2026-10-28



Una inyeccion ocurre cuando datos no confiables alteran la sintaxis o el significado de una consulta o instruccion interpretada.



Priorizar APIs seguras y mecanismos parametrizados. Aplicar validacion positiva de entradas cuando corresponda. Si no existe una API segura, el escape debe ser especifico del contexto y del interprete.



No asumir que una entrada es segura unicamente porque supera una validacion superficial.



## Regla 5: Prevenir exposicion de credenciales y secretos



Documento fuente: MITRE CWE-798

Seccion: Use of Hard-coded Credentials

URL fuente: https://cwe.mitre.org/data/definitions/798.html

Fecha de revision: 2026-10-28



Documento complementario: OWASP Secrets Management Cheat Sheet

URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html



Existe riesgo cuando contraseñas, tokens, claves API o credenciales reales se almacenan directamente en el codigo fuente o en archivos de configuracion que pueden exponerse.



Durante la revision, buscar patrones como:



```python

PASSWORD = "..."

API_KEY = "..."

SECRET_KEY = "..."

TOKEN = "..."

```



Tambien revisar credenciales incluidas en conexiones a bases de datos, servicios externos y configuraciones.



Recomendar:



- Utilizar variables de entorno.

- Utilizar gestores de secretos.

- No publicar credenciales en repositorios.

- Revocar y rotar inmediatamente los secretos expuestos.

- Aplicar el principio de minimo privilegio.



IMPORTANTE:



No considerar automaticamente una cadena de ejemplo, una contraseña ficticia o un marcador como una credencial real expuesta. Evaluar el contexto y la evidencia disponible.



## Regla 6: Prevenir Path Traversal y acceso inseguro a archivos



Documento fuente: MITRE CWE-22

Seccion: Improper Limitation of a Pathname to a Restricted Directory

URL fuente: https://cwe.mitre.org/data/definitions/22.html

Fecha de revision: 2026-10-28



Documento complementario: OWASP Path Traversal

URL fuente: https://owasp.org/www-community/attacks/Path_Traversal



Existe riesgo cuando una aplicacion utiliza rutas o nombres de archivos controlados por usuarios sin comprobar que el archivo solicitado permanece dentro del directorio permitido.



Patrones que deben revisarse:



```python

open(ruta, "r")

open(nombre_archivo, "w")

os.path.join(directorio, nombre)

Path(directorio) / nombre

pathlib.Path

```



Prestar especial atencion a:



- Uso de ../ para acceder a directorios superiores.

- Rutas absolutas proporcionadas externamente.

- Separadores de directorios manipulados.

- Rutas codificadas o normalizadas incorrectamente.

- Archivos simbolicos que puedan escapar del directorio permitido.



Recomendar:



- Resolver y normalizar las rutas.

- Comprobar que la ruta final permanece dentro del directorio autorizado.

- Aplicar listas de nombres permitidos cuando corresponda.

- Controlar los permisos de acceso.

- Considerar los enlaces simbolicos durante la validacion.



No considerar automaticamente cualquier llamada a open() como una vulnerabilidad. Comprobar si la ruta puede ser controlada por una fuente no confiable.
