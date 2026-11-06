# Levantamiento de requisitos y preguntas del caso

**Estado:** instrumento preparado y reconstrucción documental actual. No se
aportaron respuestas de una entrevista/encuesta ni notas originales de Fase 1.
Este documento no acredita que se haya realizado ese levantamiento.

Responsable: Ronald Yépez. Fecha de preparación: 5 de noviembre de 2026.
Fuente de las respuestas documentales: código y documentos de `65675e2`.
No se atribuyen estas respuestas a usuarios entrevistados.

## Instrumento de 18 preguntas

| ID | Pregunta para el participante | Situación documentada / dato por confirmar | Relación |
|---|---|---|---|
| L01 | ¿Qué dificultad encuentra al revisar seguridad de Python? | La propuesta plantea tiempo y trazabilidad; falta validación con usuario | HU-01 |
| L02 | ¿Quién usaría la herramienta y con qué experiencia? | Usuarios previstos: desarrolladores, QA y evaluadores; falta caracterización real | Propuesta |
| L03 | ¿Cómo realiza hoy la revisión y cuánto tarda? | Sin medición del proceso actual; respuesta pendiente | RNF-14 |
| L04 | ¿Prefiere pegar código, cargar `.py`, ZIP o GitHub? | Las cuatro entradas existen; preferencia del participante pendiente | HU-01–04 |
| L05 | ¿Qué tamaño y cantidad de archivos necesita revisar? | Hay límites implementados; adecuación a necesidades reales pendiente | RNF-07–09 |
| L06 | ¿Necesita repositorios privados o varios lenguajes? | El alcance actual solo cubre Python y repositorios públicos | HU-04 |
| L07 | ¿Qué información necesita para entender un hallazgo? | Línea, severidad, descripción y corrección en el contrato; validación de utilidad pendiente | RF-05 |
| L08 | ¿Cómo comprobaría que una referencia respalda el hallazgo? | La interfaz resuelve IDs por informe; requiere revisión humana de pertinencia | HU-05 |
| L09 | ¿Qué debe ocurrir cuando no hay evidencia suficiente? | Abstención con motivo; aceptación de este comportamiento pendiente | HU-06 |
| L10 | ¿Cómo desea distinguir una regla estática de una explicación de IA? | Paneles y procedencia separados, sin citas inventadas | HU-08 |
| L11 | ¿Qué espera ver cuando Gemini falla? | Estado parcial si hay evidencia útil; no se presenta código seguro | HU-09 |
| L12 | ¿Necesita exportar resultados y en qué formato? | JSON implementado; otros formatos y preferencia pendientes | HU-10 |
| L13 | ¿Qué información de su código no autoriza enviar a un proveedor? | Aviso excluye secretos y material confidencial; requisitos concretos pendientes | RS-07 |
| L14 | ¿Desea inspección de solo lectura o cambios automáticos? | MVP de solo lectura; no aplica correcciones ni ejecuta código | RS-01 |
| L15 | ¿Qué tiempo de espera considera aceptable? | No hay SLA validado con usuarios; no confundir timeout con latencia prometida | RNF |
| L16 | ¿Necesita que las fuentes sobrevivan a un reinicio? | Volumen e índice persistentes; evidencia de continuidad disponible | HU-12 |
| L17 | ¿Desde qué dispositivo y navegador usará el producto? | Interfaz responsive; perfil real del participante pendiente | RNF-15 |
| L18 | ¿Con qué ejemplos decidiría que el producto le resulta útil? | Hay dataset sintético y pruebas; casos de aceptación del participante pendientes | Evaluación |

## Registro de aplicación, aún sin completar

| Campo | Valor |
|---|---|
| Fecha real, modalidad y lugar | No aportados |
| Entrevistador | Por registrar al realizar o recuperar la actividad |
| Participante / rol y consentimiento de registro | No aportados; usar identificador anónimo si corresponde |
| Respuestas L01–L18 | No aportadas |
| Evidencia original autorizada | No aportada |
| Conclusiones validadas con participante | Pendientes |

Para completar: conservar respuestas reales por ID, separar cita y síntesis,
anotar necesidades aceptadas/rechazadas y su motivo, enlazar los requisitos
afectados y registrar fecha real. Si la actividad se realiza ahora, identificarla
como levantamiento complementario de Entrega 4; no fecharla retrospectivamente.

Los casos sintéticos de `eval/` y esta FAQ documental no reemplazan evidencia de
Fase 1. Si no existen originales, explicar la ausencia al docente y acordar la
forma de subsanación.
