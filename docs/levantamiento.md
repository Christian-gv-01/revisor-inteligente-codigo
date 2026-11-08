# Levantamiento de requisitos y preguntas del caso

**Estado:** instrumento completado con un ejercicio de respuestas simuladas para documentar hipótesis de requisitos. No constituye evidencia de entrevistas reales.

**Responsable del instrumento:** Ronald Yépez.
**Fecha de elaboración documental:** 7 de noviembre de 2026.
**Fecha de referencia del ejercicio simulado:** 17 de octubre de 2026.
**Proyecto:** CODEGUARD – Revisor Inteligente de Código Python.
**Participantes:** cinco perfiles ficticios identificados mediante códigos anónimos.

**Nota metodológica:** las respuestas que aparecen a continuación son simuladas. No se atribuyen a personas reales ni se presentan como entrevistas efectivamente realizadas.

---

## 1. Objetivo del levantamiento

Identificar las necesidades, expectativas y dificultades que pueden experimentar los desarrolladores y revisores al analizar código Python, especialmente en la detección de vulnerabilidades, interpretación de resultados y trazabilidad de evidencias.

El levantamiento sirve como referencia para organizar los requisitos funcionales y no funcionales de CODEGUARD.

## 2. Perfiles considerados en la simulación

| Código | Perfil | Experiencia considerada |
|---|---|---|
| P01 | Desarrollador Python | Desarrollo de aplicaciones Python |
| P02 | Estudiante de Ingeniería de Software | Programación y proyectos académicos |
| P03 | Analista de QA | Pruebas y validación de software |
| P04 | Desarrollador Backend | APIs y servicios con Python |
| P05 | Revisor de código y seguridad | Revisión de calidad y vulnerabilidades |

## 3. Instrumento de 18 preguntas y respuestas simuladas

| ID | Pregunta | P01 | P02 | P03 | P04 | P05 |
|---|---|---|---|---|---|---|
| L01 | ¿Qué dificultad encuentra al revisar seguridad de Python? | Detectar vulnerabilidades complejas. | Comprender errores de seguridad. | Revisiones manuales lentas. | Identificar problemas entre archivos. | Evitar falsos positivos. |
| L02 | ¿Quién usaría la herramienta y con qué experiencia? | Desarrolladores. | Estudiantes. | Personal QA. | Desarrolladores backend. | Revisores de código. |
| L03 | ¿Cómo realiza hoy la revisión y cuánto tarda? | Revisión manual y herramientas. | Lectura del código. | Pruebas automatizadas. | Ruff y Bandit. | Análisis estático y manual. |
| L04 | ¿Prefiere pegar código, cargar `.py`, ZIP o GitHub? | Todas las opciones. | Pegar código y `.py`. | ZIP. | `.py` y GitHub. | Todas las opciones. |
| L05 | ¿Qué tamaño y cantidad de archivos necesita revisar? | Proyectos medianos. | Archivos pequeños. | Proyectos completos. | Varios archivos. | Repositorios medianos y grandes. |
| L06 | ¿Necesita repositorios privados o varios lenguajes? | Repositorios privados. | Principalmente Python. | Varios archivos Python. | Repositorios privados. | Más lenguajes en el futuro. |
| L07 | ¿Qué información necesita para entender un hallazgo? | Línea y solución. | Explicación sencilla. | Severidad y evidencia. | Ubicación y recomendación. | Regla y justificación. |
| L08 | ¿Cómo comprobaría que una referencia respalda el hallazgo? | Consultando la fuente. | Revisando el enlace. | Comprobando la referencia. | Verificando la regla. | Contrastando la evidencia. |
| L09 | ¿Qué debe ocurrir cuando no hay evidencia suficiente? | Informar la falta de evidencia. | Explicar la incertidumbre. | Mostrar resultado parcial. | No inventar vulnerabilidades. | Abstenerse de clasificar. |
| L10 | ¿Cómo desea distinguir una regla estática de una explicación de IA? | Paneles separados. | Etiquetas diferentes. | Identificar procedencia. | Diferenciar herramientas. | Mostrar reglas y fuentes. |
| L11 | ¿Qué espera ver cuando Gemini falla? | Conservar resultados disponibles. | Explicar el error. | Mostrar análisis parcial. | Permitir reintento. | Informar el fallo. |
| L12 | ¿Necesita exportar resultados y en qué formato? | JSON. | JSON. | JSON y PDF. | JSON. | JSON y reportes. |
| L13 | ¿Qué información de su código no autoriza enviar a un proveedor? | Contraseñas y claves. | Código privado. | Datos confidenciales. | Variables de entorno. | Credenciales y secretos. |
| L14 | ¿Desea inspección de solo lectura o cambios automáticos? | Solo lectura. | Solo lectura. | Solo lectura. | Solo lectura. | Solo lectura. |
| L15 | ¿Qué tiempo de espera considera aceptable? | Menos de un minuto. | Respuesta rápida. | Depende del proyecto. | Tiempo controlado. | Mostrar progreso y espera. |
| L16 | ¿Necesita que las fuentes sobrevivan a un reinicio? | Sí. | Sí. | Sí. | Sí. | Sí. |
| L17 | ¿Desde qué dispositivo y navegador usará el producto? | Computadora y Chrome. | Computadora y navegador. | Computadora y Chrome. | Computadora. | Computadora y varios navegadores. |
| L18 | ¿Con qué ejemplos decidiría que el producto le resulta útil? | Detectar errores reales. | Comprender vulnerabilidades. | Comparar resultados. | Revisar proyectos completos. | Obtener hallazgos verificables. |

## 4. Análisis de las respuestas

### 4.1 Facilidad de uso

Los perfiles simulados reflejan la importancia de disponer de una interfaz sencilla que permita introducir código directamente o cargar archivos y proyectos.

CODEGUARD contempla diferentes mecanismos de entrada para facilitar el proceso de revisión.

### 4.2 Información y trazabilidad

Se identifica como necesidad de diseño mostrar información suficiente para comprender cada hallazgo:

- Ubicación exacta en el código.
- Severidad asignada.
- Descripción del problema.
- Recomendación de corrección.
- Regla estática o referencia documental relacionada.

Esto coincide con el objetivo de proporcionar resultados comprensibles y verificables.

### 4.3 Confianza en los resultados

Se considera importante diferenciar los resultados de Ruff y Bandit de las explicaciones generadas mediante Gemini y RAG.

También se destaca que el sistema debe informar cuando no dispone de evidencia suficiente y evitar presentar una conclusión incierta como una vulnerabilidad confirmada.

### 4.4 Seguridad y privacidad

Los perfiles simulados priorizan proteger contraseñas, credenciales, variables de entorno y código confidencial.

El producto mantiene un enfoque de análisis de solo lectura, sin ejecutar el código recibido ni aplicar correcciones automáticamente.

## 5. Conclusiones del ejercicio

**Conclusión 1. Interfaz y accesibilidad**

Una herramienta de revisión de código debe permitir diferentes formas de entrada y presentar los resultados de manera clara para desarrolladores con distintos niveles de experiencia.

**Conclusión 2. Evidencia verificable**

La ubicación del hallazgo, su severidad y la procedencia de las reglas son elementos importantes para facilitar la revisión y reducir interpretaciones incorrectas.

**Conclusión 3. Diferenciación de herramientas e inteligencia artificial**

Es necesario separar las alertas deterministas de Ruff y Bandit de las explicaciones generadas por Gemini y RAG. La herramienta también debe gestionar los casos en los que el proveedor de IA no responde.

**Conclusión 4. Mejoras futuras**

Se identifican como posibles mejoras ampliar el soporte para repositorios privados, incorporar otros lenguajes, mejorar la experiencia de exportación y optimizar los tiempos de respuesta y el consumo de recursos.

## 6. Relación con los requisitos de CODEGUARD

| Necesidad identificada | Requisito relacionado | Funcionalidad del producto |
|---|---|---|
| Diferentes entradas de código | HU-01 a HU-04 | Código, archivos, ZIP y GitHub |
| Mostrar hallazgos comprensibles | RF-05 | Severidad, ubicación y descripción |
| Consultar evidencias | HU-05 | Referencias y trazabilidad |
| Gestionar ausencia de evidencia | HU-06 | Abstención del agente |
| Diferenciar fuentes | HU-08 | Procedencia de resultados |
| Gestionar fallos de Gemini | HU-09 | Resultados parciales |
| Exportar resultados | HU-10 | Exportación JSON |
| Proteger información | RS-01 y RS-07 | Análisis de solo lectura y protección de secretos |
| Conservar información | HU-12 | Persistencia de fuentes |

## 7. Limitaciones del levantamiento

Este documento contiene un ejercicio de simulación y no resultados de entrevistas reales.

Los cinco perfiles no representan participantes identificados ni respuestas recogidas mediante una actividad de campo.

Por tanto:

- No se puede afirmar que cinco usuarios hayan validado el producto.
- Las preferencias indicadas no constituyen una muestra estadística.
- Las conclusiones son hipótesis para orientar el desarrollo.
- Se requiere aplicar el cuestionario a participantes reales para validar las necesidades identificadas.

## 8. Próximas actividades

1. Aplicar el cuestionario a un mínimo de cinco personas que revisen código Python.
2. Registrar la fecha real de aplicación y el rol de cada participante.
3. Contrastar las respuestas reales con las hipótesis documentadas.
4. Actualizar los requisitos según las necesidades confirmadas.
5. Conservar las evidencias originales y sus referencias en el repositorio.

**Resultado documental:** instrumento de 18 preguntas organizado, cinco perfiles simulados, matriz de respuestas, cuatro conclusiones y relación con los requisitos de CODEGUARD.

---

**Fin del documento.**