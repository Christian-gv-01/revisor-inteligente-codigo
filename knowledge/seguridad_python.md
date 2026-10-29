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

La funcion eval puede ejecutar expresiones construidas a partir de datos
externos. Si una persona puede controlar la entrada evaluada, puede
provocar ejecucion de codigo no prevista.

Durante la revision, comprobar si eval recibe datos controlados por el
usuario. Recomendar alternativas que no ejecuten codigo arbitrario.
ast.literal_eval limita la evaluacion a literales, pero tampoco debe
considerarse una solucion universal para entradas no confiables, porque
entradas profundamente anidadas pueden consumir demasiados recursos.

## Regla 2: Prevenir inyeccion SQL

Documento fuente: OWASP SQL Injection Prevention Cheat Sheet
Seccion: Primary Defenses y Allow-List Input Validation
URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
Fecha de revision: 2026-10-28

Las consultas SQL no deben construirse concatenando datos no confiables
dentro de la instruccion SQL.

Preferir consultas parametrizadas o sentencias preparadas para separar
la estructura de la consulta de sus valores.

Si el usuario puede elegir nombres de columnas, tablas u ordenamientos,
usar opciones fijas permitidas por la aplicacion. Validar una entrada
no sustituye la parametrizacion de la consulta.

## Regla 3: Prevenir inyeccion de comandos del sistema

Documento fuente: OWASP OS Command Injection Defense Cheat Sheet
Seccion: Defensas contra la inyeccion de comandos
URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
Fecha de revision: 2026-10-28

Existe riesgo cuando datos controlados externamente modifican el comando
del sistema que ejecuta la aplicacion.

Preferir APIs que no invoquen un interprete de comandos. No concatenar
entradas no confiables en comandos. Si una operacion del sistema es
necesaria, limitar las opciones permitidas y aplicar el principio de
minimo privilegio.

Durante la revision, buscar usos de funciones de ejecucion de comandos
y comprobar de donde proceden sus argumentos.

## Regla 4: Prevencion general de inyecciones

Documento fuente: OWASP Injection Prevention Cheat Sheet
Seccion: Injection Prevention Rules
URL fuente: https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html
Fecha de revision: 2026-10-28

Una inyeccion ocurre cuando datos no confiables alteran la sintaxis o
el significado de una consulta o instruccion interpretada.

Priorizar APIs seguras y mecanismos parametrizados. Aplicar validacion
positiva de entradas cuando corresponda. Si no existe una API segura,
el escape debe ser especifico del contexto y del interprete.

No asumir que una entrada es segura unicamente porque supera una
validacion superficial.

