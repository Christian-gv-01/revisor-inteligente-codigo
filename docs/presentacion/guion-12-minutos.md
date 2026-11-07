# Guion de doce minutos: cierre técnico y resultados reales

Preparación del 7 de noviembre de 2026. Doce diapositivas, 720 segundos
planificados, sin acreditar ensayo ni reparto. Las dos corridas reales usan `8e66b2c` y `c522c24`.
El ajuste de consumo posterior está en PR #57 y no cambia los prompts del análisis.

Integrantes confirmados: Ronald Yépez, Klever Andres Alban Cruz (Andy) y Christian
Gamboa. La base técnica final es `b6ce96c`; las métricas siguientes conservan sus
commits de evaluación. El nombre completo se incorpora sin cambiar resultados.

## 1. CODEGUARD — 30 segundos

CODEGUARD es un revisor asistido de Python. Combina herramientas estáticas,
recuperación documental y un agente supervisado. Hoy diferenciamos tres cosas:
lo implementado y probado, los resultados reales de Gemini y los límites que
siguen abiertos. No ejecutamos el código recibido ni aplicamos cambios al
repositorio. La evidencia conserva versión y procedencia.

Fuente: docs/37-cierre-verificado.md.

## 2. Una revisión útil necesita evidencia — 60 segundos

Un desarrollador puede introducir riesgos al concatenar entradas en consultas,
ejecutar comandos o evaluar texto como código. El producto ayuda a localizar
el patrón y explicar la recomendación. Mostrar una consulta SQL concatenada y
la separación entre valores y estructura. El valor esperado es facilitar la
revisión; todavía no tenemos un estudio con usuarios que mida tiempo ahorrado.
Un hallazgo no certifica explotabilidad y la ausencia de alertas no demuestra
que el programa sea seguro. Las recomendaciones necesitan contexto y revisión.

Fuente: docs/01-propuesta.md y docs/02-requisitos.md.

## 3. Del código al informe — 60 segundos

El frontend valida la entrada y utiliza una API del mismo origen. Para código
pegado y .py solicita agente v2. Ruff/Bandit y AST producen evidencia; el
planificador elige herramientas permitidas y la síntesis combina código,
evidencia y documentos recuperados. El backend valida estructura, ubicaciones
y referencias. ZIP y GitHub conservan el flujo directo por archivo, con un
presupuesto aprobado antes de la generación. El índice está en ChromaDB y las
propuestas temporales en SQLite. Las claves solo existen en el backend.

Fuente: docs/03-arquitectura.md y docs/tratamiento-datos.md.

## 4. Recorrido del agente v2 — 70 segundos

El agente siempre realiza la inspección inicial. Después puede detectar
llamadas sensibles, revisar SQL, ampliar contexto hasta seis líneas por lado,
buscar referencias por categoría permitida o finalizar. Los resultados
participan en la decisión siguiente y la síntesis. El máximo es cuatro pasos
totales; la interfaz principal solicita tres y esta evaluación solicitó cuatro.
No tiene shell ni ejecución libre. La traza diferencia la elección del modelo,
la inspección automática y el respaldo local. Una herramienta fallida no aparece
como éxito. De veinte casos reales de c522c24, ocho finalizaron anticipadamente; eso no
permite calcular ahorro causal sin una comparación equivalente de consumo.

Fuente: docs/08-agente.md, contrato-agente-v2 y resultados de la corrida real.

## 5. La aprobación ocurre después de revisar — 70 segundos

La corrección propuesta se muestra junto al original. Generar la previsualización
puede consumir Gemini antes de la aprobación. La confirmación autoriza únicamente
la descarga de esa copia. El usuario debe marcar una autorización explícita;
sesión, identificador y hashes la vinculan al contenido revisado. Rechazar no
descarga ni modifica el original. La propuesta caduca y las decisiones repetidas
o contradictorias se resuelven con reglas de idempotencia y conflicto. No
presentamos las pruebas con proveedor simulado como calidad de correcciones
reales. La interfaz pública ya permite este recorrido y la decisión HTTP real conservó
exactamente el contenido revisado, con repetición idempotente y conflicto opuesto.

Fuente: docs/20-contrato-confirmacion-humana.md y docs/23-integracion-confirmacion-qa.md.

## 6. Presupuesto ZIP/GitHub — 70 segundos

Esta autorización es distinta de descargar una corrección. Primero se valida
el proyecto y se muestra la lista de archivos, modelo, análisis previstos,
intentos máximos, plazo y caducidad. Preparar GitHub sí consulta su API pública,
pero no Gemini. Aprobar autoriza solo la instantánea revisada; rechazar no añade
llamadas generativas. Se admiten cinco Python y doce mil caracteres combinados.
El plazo cooperativo y el máximo de intentos son límites, no una cotización en
dólares ni una predicción de duración. Dejar de esperar en el navegador no revoca
un análisis que ya se aprobó. Backend e interfaz están habilitados en la versión pública comprobada. El cierre
expuso un contador perdido entre presupuestos anidados, corregido en PR #57.

Fuente: docs/28-presupuesto-proyectos.md y smoke Docker.

## 7. Severidad verificable — 60 segundos

Se distingue severidad original, confianza y resultado. La prioridad utiliza
pesos operativos; no son probabilidades. La política YAML puede derivar crítica
cuando Bandit informa alta severidad y alta confianza. Para heredar, Gemini
debe citar una regla ofrecida, no ambigua y en la misma línea validada. El
backend calcula el resultado y reconstruye la auditoría; el modelo no puede
inventarla. Nunca se reduce la severidad original. Una ventana cercana no basta.
La interfaz y el JSON conservan original, reglas y resultado para revisión.

Fuente: docs/35-severidad-derivada-herencia.md.

## 8. Comparación real — 60 segundos

Ejecutamos cuarenta análisis sobre c522c24, con los mismos veinte casos y orden
alternado. La directa completó 17 de 20 y el agente 14 de 20. Solo trece pares
completaron ambas rutas: en ese subconjunto F1 fue 1,0 para las dos. Se conservan
tres y seis parciales. La media global fue 10,34 y 22,62 segundos, con 21 y 71
intentos SDK. Los tokens totales son desconocidos porque hubo intentos sin respuesta.
La corrida previa completa se conserva: F1 0,957 y 0,762. El nuevo subconjunto no
permite afirmar una mejora causal ni generalización. El agente no demostró mayor
precisión y tuvo menor completitud. Nunca presentamos los parciales como aciertos.

Fuente: docs/evidencias/semana-4/postmerge-c522c24-20261107/ y corrida histórica.

## 9. Conocimiento y cobertura — 60 segundos

El inventario conserva ocho originales oficiales y seis reglas curadas. El índice
activo coincidió con el fuente y tuvo la misma huella durante y al final de las
pruebas; faltó la observación inicial, que se declara. La revisión asistida de los
18 hallazgos completos verificó pertinencia de las citas, sin ejecutar parches ni
sustituir una revisión humana independiente. El A/B del planificador recorrió seis
pares sin y con evidencia estática: cinco comparables, uno incompleto por 503 y dos
cambios de decisión. Demuestra influencia del contexto en esa muestra, no mayor
precisión. Las métricas documentales históricas se conservan separadas.

Fuente: docs/04-fuentes.md y docs/18-comparacion-semanas-3-4.md.

## 10. Pruebas de software — 60 segundos

El cierre con PR #57 aprobó 589 pruebas backend, 146 frontend y 80 de QA/evaluadores.
Las específicas ya forman parte de esos totales. La integración HTTP completó
24 de 24 con estático y 19 aplicables sin él; cinco requieren ese componente.
Las 24 HTTP omitidas en la suite unitaria no se cuentan como aprobadas allí.
Estas pruebas usan Gemini y GitHub simulados. Verifican contratos, conservación
de hallazgos, abstención, sesiones, límites y regresiones; las cifras de precisión
proceden exclusivamente de la corrida real descrita antes.

Fuente: docs/37-cierre-verificado.md y registros de CI del candidato.

## 11. Trazabilidad documental — 70 segundos

El documento 08 explica el agente y el 17 remite al principal. Los requisitos
incluyen las ocho historias solicitadas, con criterios Dado/Cuando/Entonces, y
el inventario mantiene procedencia y hashes. README, decisiones y privacidad
reflejan sesiones, almacenamiento temporal y confirmaciones. La ficha del docente
revisaba 605d142 del día anterior; la tabla de cierre relaciona observaciones con
commits y pruebas posteriores. Conservar históricos permite reconocer errores
y cambios. El ZIP se genera desde una revisión Git exacta, con manifiesto,
integridad y límite de veinte MB; generarlo no acredita envío al portal.

Fuente: docs/37-cierre-verificado.md y scripts/empaquetar_entrega.py.

## 12. Conclusión — 50 segundos

Demostramos un agente acotado con decisiones trazables y confirmaciones públicas.
El contexto cambió dos de cinco decisiones comparables, pero el agente no demostró
mayor precisión y consumió más intentos y tiempo. Conservamos las dos corridas y
sus fallos. El cierre corrigió cobertura y contadores con regresiones reproducibles.
El ensayo oral, la instalación independiente, las aceptaciones y el envío al portal
son actividades humanas pendientes. Entregamos resultados verificables y sus límites,
sin afirmar que una batería de software certifica la seguridad de cualquier programa.

Fuente: docs/37-cierre-verificado.md y revisión asistida de citas.
