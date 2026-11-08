# Levantamiento de requisitos y preguntas del caso

> **Levantamiento complementario documentado el 8 de noviembre de 2026**, con cinco cuestionarios cuyas respuestas están fechadas el **7 de noviembre de 2026**. Se realiza como subsanación posterior a la Semana 1 y **no** se presenta como entrevista aplicada durante la semana inicial. Los datos provienen del Word entregado por el equipo; no existe un registro independiente de fecha de aplicación o consentimiento en este repositorio. Evitar publicar datos identificables sin autorización de los participantes.

**Proyecto:** CODEGUARD – Revisor Inteligente de Código Python
**Responsable del instrumento:** Ronald Yépez
**Fecha registrada en los cuestionarios:** 7 de noviembre de 2026
**Fuente:** cuestionario respondido entregado por el equipo (`PROYECTO CODEGUARD_PREGUNTAS_RESPUESTAS.docx`).

## 1. Objetivo

Identificar necesidades, dificultades y expectativas de personas con distintos perfiles de desarrollo y revisión de software respecto al análisis de seguridad de código Python. Las respuestas se utilizan para contrastar el alcance actual de CODEGUARD y orientar mejoras.

## 2. Participantes registrados

| Código | Participante | Rol o profesión | Experiencia en Python | Fecha registrada |
|---|---|---|---:|---|
| P01 | Luis Lozada | Desarrollador Backend | 3 años | 07/11/2026 |
| P02 | Juan Muñoz | Desarrollador de Software Freelance | 4 años | 07/11/2026 |
| P03 | Ángel López | Administrador de Sistemas | 1 año y medio | 07/11/2026 |
| P04 | Alex Martínez | Ingeniero de Software Fullstack | 2 años | 07/11/2026 |
| P05 | Joel Sánchez | Estudiante de Ingeniería de Software | 1 año | 07/11/2026 |

## 3. Instrumento y respuestas registradas

Las siguientes respuestas se transcriben del documento entregado por el equipo. Se conserva el sentido de cada respuesta y se organizan por pregunta para facilitar su comparación.

| ID | Pregunta | P01 – Luis Lozada | P02 – Juan Muñoz | P03 – Ángel López | P04 – Alex Martínez | P05 – Joel Sánchez |
|---|---|---|---|---|---|---|
| L01 | ¿Qué dificultad encuentras al revisar la seguridad de código Python? | Manejo incorrecto de dependencias de terceros y vulnerabilidades en paquetes desactualizados. | Falta de tiempo para auditar proyectos grandes y complejos heredados. | No conocer a fondo todas las vulnerabilidades avanzadas en scripts de automatización. | Detectar malas configuraciones en frameworks web como Flask o FastAPI. | No saber identificar cuáles son los errores o vulnerabilidades comunes en seguridad. |
| L02 | ¿Quién consideras que utilizaría una herramienta como CODEGUARD y con qué experiencia? | Desarrolladores junior y estudiantes de Ingeniería de Software. | Programadores backend con experiencia intermedia. | Personal de soporte y desarrolladores que escriben scripts rápidos. | Desarrolladores junior y mid-level. | Estudiantes y personas que están aprendiendo a programar. |
| L03 | ¿Cómo realizas actualmente la revisión de seguridad del código y cuánto tiempo te toma? | Revisión manual y herramientas estáticas básicas; 20–30 minutos por archivo grande. | Linters automatizados en procesos locales; un par de minutos. | Revisión manual línea por línea; más de 30 minutos. | Extensiones del editor; un par de minutos. | No realiza revisiones formales de seguridad; solo prueba que el código funcione. |
| L04 | ¿Qué método prefieres para revisar código: pegarlo directamente, cargar un archivo `.py`, subir un ZIP o conectar GitHub? | Cargar archivo `.py` y conectar directamente con GitHub. | Conectar directamente con repositorios de GitHub. | Pegar el código directamente o subir un archivo `.py`. | Cargar archivos `.py` o subir archivos ZIP. | Pegar el código directamente en la web o subir un archivo `.py`. |
| L05 | ¿Qué tamaño y cantidad de archivos necesitas revisar normalmente? | Scripts de unas 300 líneas, con un promedio de 5 a 10 archivos por revisión. | Repositorios completos de proyectos web medianos. | Scripts cortos de automatización, de menos de 200 líneas. | Proyectos web medianos, de 10 a 15 archivos. | Archivos académicos o scripts pequeños, de menos de 100 líneas. |
| L06 | ¿Necesitas revisar repositorios privados o trabajar con otros lenguajes además de Python? | Sí, repositorios privados y ocasionalmente JavaScript. | Sí, repositorios privados de manera indispensable. | No, principalmente scripts sueltos en Python. | A veces repositorios privados y código web híbrido. | No, solo proyectos académicos en Python. |
| L07 | ¿Qué información necesitas para comprender correctamente un problema de seguridad detectado? | Línea exacta, tipo de vulnerabilidad y ejemplo de solución. | Nivel de severidad y ruta del archivo vulnerable. | Explicación sencilla y en lenguaje claro de qué está fallando. | Ejemplos prácticos de código seguro frente al código vulnerable. | Explicación detallada de por qué es un error, porque está aprendiendo. |
| L08 | ¿Cómo comprobarías que una referencia o fuente respalda realmente un hallazgo? | Verificando que apunte a bases de datos oficiales como OWASP o CVE. | Mediante enlaces directos a estándares de seguridad reconocidos. | Que la explicación sea lógica y fácil de verificar. | Verificando que los enlaces de referencia funcionen correctamente. | Revisando que la documentación oficial respalde la explicación. |
| L09 | ¿Qué debería hacer la herramienta cuando no encuentra evidencia suficiente para confirmar una vulnerabilidad? | Mostrar una advertencia en lugar de presentar un falso positivo como definitivo. | Marcarlo como una sugerencia de baja prioridad. | Omitir el aviso para no saturar. | Descartar el reporte para evitar falsas alarmas. | Avisar que no hay seguridad completa para no confundir al usuario. |
| L10 | ¿Cómo te gustaría distinguir los resultados de herramientas estáticas de las explicaciones generadas por inteligencia artificial? | Con etiquetas visuales o colores diferentes en la interfaz. | Con paneles o pestañas independientes. | Con textos explicativos fáciles de leer. | Mediante iconos y un diseño visual distintivo. | Con un apartado de chat donde la IA explique el detalle. |
| L11 | ¿Qué esperas que suceda si el servicio de inteligencia artificial Gemini presenta un error o deja de responder? | Que la aplicación muestre un aviso de reintento temporal. | Un aviso claro de caída temporal con opción de reintentar. | Un mensaje emergente sencillo en la pantalla. | Que mantenga accesibles los resultados del análisis estático. | Un aviso en pantalla para volver a intentar después. |
| L12 | ¿Necesitas exportar los resultados? ¿Qué formato prefieres? | Sí, PDF o reporte Markdown. | Sí, JSON o PDF. | No es necesario; basta con verlos en pantalla. | Sí, PDF. | No es obligatorio; basta con verlos en la web. |
| L13 | ¿Qué información de tu código consideras confidencial y no permitirías enviar a un proveedor externo? | Llaves de API y credenciales de bases de datos. | Tokens de autenticación y lógica de negocio privada. | Contraseñas y accesos a servidores internos. | Claves privadas y credenciales de acceso. | Ninguna en particular; son proyectos de práctica universitaria. |
| L14 | ¿Prefieres que la herramienta solamente analice el código o que también realice correcciones automáticas? | Que sugiera la corrección y permita aplicarla opcionalmente. | Análisis detallado con sugerencias de código seguro. | Que proporcione el bloque de código corregido para copiar y pegar. | Correcciones sugeridas que se puedan aplicar con un clic. | Que enseñe cómo corregirlo con ejemplos claros. |
| L15 | ¿Cuánto tiempo considerarías aceptable esperar para obtener un análisis? | Menos de 10 segundos. | Menos de 15 segundos. | Menos de 5 segundos. | Máximo 10 segundos. | Alrededor de 5 a 10 segundos. |
| L16 | ¿Consideras importante que las fuentes y evidencias consultadas se conserven después de reiniciar el sistema? | Sí, para llevar un historial de auditoría. | Sí, para documentar las entregas. | No es prioritario. | Sí, para consultarlas más tarde. | Sería útil para repasar después. |
| L17 | ¿Desde qué dispositivo y navegador utilizarías normalmente la herramienta? | Laptop con Windows y Google Chrome. | PC de escritorio y Google Chrome. | Laptop personal y Microsoft Edge. | Laptop personal y Google Chrome. | Laptop y Google Chrome. |
| L18 | ¿Qué características tendría que cumplir CODEGUARD para que consideres útil y confiable su análisis? | Rapidez, precisión y explicaciones técnicas claras. | Confiabilidad en la detección de fallos críticos y seguridad de los datos. | Que sea sumamente fácil de usar y sin complicaciones. | Interfaz limpia y respuestas rápidas. | Que sea didáctico y fácil de entender para alguien que aprende. |

## 4. Análisis de las respuestas

### 4.1 Formas de entrada y alcance de los proyectos

Las preferencias varían según el perfil: se mencionan carga de archivos `.py`, pegado de código, archivos ZIP y conexión con GitHub. También aparecen necesidades de revisar varios archivos y repositorios medianos. Dos participantes señalan expresamente repositorios privados y otros mencionan ocasionalmente código JavaScript o web híbrido.

**Implicación para CODEGUARD:** mantener claras las entradas que el producto soporta actualmente y registrar repositorios privados y otros lenguajes como necesidades de evolución, no como capacidades ya disponibles si todavía no están implementadas.

### 4.2 Hallazgos comprensibles y verificables

Las respuestas solicitan ubicación exacta, tipo de vulnerabilidad, severidad, ruta del archivo, explicación sencilla o técnica y ejemplos de corrección. Para verificar las referencias, se mencionan fuentes oficiales como OWASP, CVE, estándares reconocidos y enlaces funcionales.

**Implicación para CODEGUARD:** cada hallazgo debe mostrar su ubicación y explicación, diferenciar la severidad y conservar la procedencia de las reglas o referencias. Las referencias deben poder comprobarse y no deben presentarse como respaldo si no son pertinentes.

### 4.3 Incertidumbre y disponibilidad de la IA

Los participantes prefieren advertencias, prioridad baja, omisión o descarte cuando no existe evidencia suficiente, para evitar falsas alarmas. Si Gemini falla, esperan un aviso y posibilidad de reintento; también se solicita conservar los resultados estáticos disponibles.

**Implicación para CODEGUARD:** informar la falta de evidencia, evitar afirmar que una vulnerabilidad está confirmada sin respaldo y conservar los resultados estáticos útiles cuando falle el servicio de IA.

### 4.4 Privacidad, experiencia y rendimiento

Se identifican como datos sensibles las llaves de API, credenciales, tokens, contraseñas, accesos internos y lógica de negocio privada. Los tiempos esperados indicados oscilan entre menos de 5 y menos de 15 segundos. Los perfiles también muestran necesidades distintas: desde explicaciones didácticas hasta reportes PDF, Markdown o JSON. Cuatro participantes expresan interés en sugerencias o aplicación de correcciones; uno prefiere únicamente aprender cómo corregir el problema.

**Implicación para CODEGUARD:** informar claramente el tratamiento del código enviado a servicios externos, proteger secretos, no prometer tiempos que no hayan sido medidos y mantener las correcciones automáticas fuera del alcance actual de solo lectura hasta que exista un mecanismo explícito de revisión y autorización humana.

## 5. Conclusiones del levantamiento

**Conclusión 1. Diversidad de entradas y proyectos.**\
Las respuestas muestran preferencias por pegar código, cargar archivos `.py`, subir ZIP y conectar GitHub. También existe interés en repositorios privados y proyectos con varios archivos. Se confirma la importancia de documentar con precisión las entradas disponibles y considerar la ampliación de repositorios privados y lenguajes como trabajo futuro.

**Conclusión 2. Explicaciones y referencias verificables.**\
Los participantes necesitan que los hallazgos indiquen dónde está el problema, cuál es su severidad y cómo comprenderlo o corregirlo. También esperan referencias comprobables, preferentemente oficiales. CODEGUARD debe priorizar la trazabilidad y evitar referencias que no respalden el hallazgo.

**Conclusión 3. Confianza, privacidad y manejo de fallos.**\
Las respuestas destacan la protección de credenciales y código privado, la necesidad de advertir cuando no existe evidencia suficiente y la conservación de resultados estáticos si Gemini falla. Se debe mantener la separación entre resultados de herramientas estáticas y explicaciones de IA.

**Conclusión 4. Mejoras de experiencia y alcance controlado.**\
Se identifican expectativas de rapidez, interfaz sencilla, explicaciones didácticas y exportación en distintos formatos. También se solicitan correcciones asistidas, pero el producto actual mantiene un enfoque de solo lectura. Estas solicitudes deben tratarse como oportunidades de evolución y no como funcionalidades ya entregadas.

## 6. Relación con los requisitos de CODEGUARD

| Necesidad observada | Requisito o área relacionada | Aplicación en el producto |
|---|---|---|
| Diferentes formas de introducir código | HU-01 a HU-04 | Entrada de código, archivos, ZIP y GitHub según el alcance implementado. |
| Ubicación, severidad y explicación | RF-05 | Presentación estructurada de hallazgos. |
| Referencias verificables | HU-05 | Consulta y trazabilidad de evidencias. |
| Ausencia de evidencia suficiente | HU-06 | Abstención o advertencia sin afirmar una vulnerabilidad no confirmada. |
| Diferenciar herramientas estáticas e IA | HU-08 | Separación de procedencia de resultados. |
| Fallos de Gemini | HU-09 | Aviso de error y conservación de resultados estáticos útiles. |
| Exportación | HU-10 | Exportación JSON disponible; PDF y Markdown quedan sujetos al alcance implementado. |
| Protección de código y secretos | RS-01 y RS-07 | Análisis de solo lectura y medidas de protección de información. |
| Persistencia de fuentes | HU-12 | Conservación de evidencias para consultas posteriores. |

## 7. Alcance y consideraciones

- Este documento organiza las cinco respuestas contenidas en el archivo de cuestionarios entregado por el equipo.
- La fecha consignada para cada respuesta es el 07/11/2026.
- Los nombres, roles y experiencia se reproducen conforme al documento fuente.
- Las preferencias expresadas no constituyen por sí solas una medición estadística ni una prueba de precisión técnica del producto.
- Las respuestas sobre funciones deseadas no significan que esas funciones estén implementadas.
- Las conclusiones se limitan a las respuestas registradas y se utilizan para orientar la revisión de requisitos.

## 8. Resultado

Se documentan cinco participantes, 18 preguntas, 90 respuestas individuales, el análisis de necesidades, cuatro conclusiones y su relación con los requisitos de CODEGUARD.

## Fuente documental de las respuestas

Las respuestas individuales originales se conservan en el [cuestionario original de Word](evidencias/semana-1/encuestas/respuestas-cuestionario-semana-1-2026-11-07.docx).
**Fin del documento.**
