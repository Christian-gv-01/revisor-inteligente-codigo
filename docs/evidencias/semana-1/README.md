# Evidencias históricas recuperadas de Semana 1

**Estado de cierre documental: 8 de noviembre de 2026.** Esta carpeta conserva los materiales recuperables y distingue fechas verificables, copias posteriores y faltantes. No es prueba automática de cumplimiento oportuno ni acta de aprobación del docente.

## Evidencias localizadas

| Archivo | Procedencia verificada | Qué demuestra / límite |
|---|---|---|
| [historial-inicial-git.txt](historial-inicial-git.txt) | Registro recuperado de `feature/backend-severidad-derivada-20261107` (commit de incorporación `f823f1f`) | Enumera primeros commits entre 20 y 22 de octubre de 2026; los cambios concretos pueden verificarse en Git |
| [decisiones-iniciales.md](decisiones-iniciales.md) | Copia **UTF-8 legible** del archivo original `docs/09-decisiones.md`, commit [`0832860`](https://github.com/Christian-gv-01/revisor-inteligente-codigo/commit/08328609d8d98507f73e8e95f81d04f0cfc61543), de 20 de octubre de 2026 | Acredita ADR iniciales como **propuestas pendientes de aprobación**; no es acta de decisión final |
| [propuesta-version-inicial.md](propuesta-version-inicial.md) | Primera propuesta **localizada** en `docs/01-propuesta.md`, commit [`74817d5`](https://github.com/Christian-gv-01/revisor-inteligente-codigo/commit/74817d5a570eedde32089b8ce5acf59c6fe06aa0), de **4 de noviembre de 2026** | Es material posterior y no acredita una propuesta redactada en Semana 1 |
| [capturas/README.md](capturas/README.md) | Descripción textual incorporada en `f823f1f` | Menciona una captura de conexión a Gemini, pero el archivo `prueba-conexion-gemini.png` **no está versionado aquí**. Sin imagen ni fecha verificable, no tratar su descripción como prueba visual |

Los textos `decisiones-iniciales.md` y `propuesta-version-inicial.md` de la rama de recuperación presentaban caracteres mal interpretados (p. ej., `├│`). Estas copias se regeneraron desde los **objetos Git originales**, preservando su contenido legible. No se reescribió la historia técnica ni se asignaron fechas retrospectivas.

## Material adicional verificado en la rama de correcciones `127522e`

El 8 de noviembre se revisaron cuatro archivos de imagen preservados en esa revisión. **Su fecha de incorporación a GitHub es posterior** al desarrollo inicial; solo se acredita una fecha de ejecución histórica cuando figura explícitamente dentro de la imagen.

| Archivo | Contenido visible y límite |
|---|---|
| [Prueba de carga ZIP](01-prueba-api-carga-zip-2026-10-22.jpg) | Swagger/FastAPI muestra respuesta HTTP 200 de análisis ZIP con dos archivos y una alerta. Se aprecia fecha **22 oct 2026** en la respuesta HTTP de la captura; no es una prueba de todo el sistema final |
| [Informe Gemini y tokens](02-informe-gemini-tokens-2026-10-21.jpg) | Informe de hallazgo por `eval()`, tokens de entrada 135, captura con fecha **21 oct 2026** |
| [Conexión Gemini](03-conexion-gemini-3-8-flash-completa.png) | Consola declara `gemini-3.8-flash`, tiempo 20,21 s, resultado `OK` y nueve tokens de entrada; **sin fecha visible verificable** |
| [Captura complementaria](04-captura-movil-conexion-gemini.jpg) | Consola muestra informe de ejemplo y tokens de entrada/salida 135/122; **sin fecha visible verificable** |

Los PNG/JPG muestran resultados observables, no acreditan por sí solos su hora de ejecución ni una sustentación académica o aprobación del equipo. No se localizaron capturas originales de primeros commits ni del PR inicial; el historial Git sustituye **solo** la trazabilidad de commits, no las imágenes inexistentes.

## Levantamiento complementario

Se integró el [instrumento respondido y análisis](../../levantamiento.md) con **cinco participantes**, **18 preguntas**, **90 respuestas registradas** y **cuatro conclusiones**. El [Word fuente](encuestas/respuestas-cuestionario-semana-1-2026-11-07.docx) contiene los cinco cuestionarios fechados el **7 nov 2026**, y el documento Markdown representa su contenido. Esta actividad es **posterior a Semana 1** y se etiqueta como levantamiento complementario. La fecha de aplicación corresponde a la declaración del documento y del equipo, no a un registro externo auditado. Confirmar autorización antes de divulgar nombres.

## Pendientes que no se deben inventar

- No se acreditó una propuesta redactada originalmente durante Semana 1; la primera localizada es del **4 nov 2026**.
- No se recuperaron capturas originales de GitHub de commits/PR de esa semana; se conserva el historial verificable.
- El ADR original del 20 oct era una propuesta, no un acta firmada de aprobación formal.
- No existe registro independiente de aplicación presencial ni consentimientos del cuestionario.

La subsanación documental completa técnicamente los apartados reclamados de evidencias y cuestionarios, **sujeta a aceptación del docente**.
