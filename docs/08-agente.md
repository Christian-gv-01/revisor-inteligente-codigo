# 08. Agente supervisado CODEGUARD

Documento principal vigente. Ronald Yépez, 7 de noviembre de 2026, sobre
`467d00e0d56a98cd758f382a5c713737eb490845` (PR #48). Consolida el diseño inicial
y la integración antes descrita en el documento 17. Los [contratos v2](contrato-agente-v2/README.md)
detallan esquemas y ejemplos. Actualización de integración sobre `4f41ebf` (PR #52): cuatro pasos v2 y contadores de uso. La referencia del código no acredita la versión activa en Railway.

## Propósito y recorrido del producto

El agente coordina inspecciones limitadas de Python, reúne evidencia estática y
documental y produce un informe revisable. Ayuda a localizar riesgos y explicar
recomendaciones. No ejecuta el programa recibido, modifica repositorios ni
certifica que el código sea seguro.

En React, **API real** y el botón de análisis para código pegado o `.py` solicitan
`POST /api/v1/agente/analizar` con `version_herramientas: "2"`. El usuario ve
hallazgos, observaciones Ruff/Bandit y **Proceso de revisión del agente**.
El JSON conserva estado, fuentes y traza. Esta aparece al terminar la petición;
la animación de espera no representa decisiones transmitidas en vivo.

ZIP/GitHub mantienen revisión directa por archivo, con presupuesto previo cuando
la función está habilitada. No tienen el bucle v2 de un único archivo. Demo de React
usa ejemplos simulados. El laboratorio `/agente/demo` es una pantalla independiente
con modos Gemini y AST local; no debe confundirse con Demo de React. Su acceso
visible se incorpora a este candidato desde el [PR #50](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/50).
No hace falta incrustarlo para conectar el agente al análisis principal.

## Herramientas y controles obligatorios

Ruff y Bandit se ejecutan una vez antes del bucle; Gemini no puede omitirlos. Sus
observaciones permanecen en `analisis_estatico`, separadas de `informe.hallazgos`
y fuentes RAG. No se suman ambas capas como vulnerabilidades diferentes ni se
inventan referencias MITRE/OWASP para alertas estáticas.

| Acción | Entrada y resultado | Alcance |
|---|---|---|
| `inspeccionar_estructura` | Código; sintaxis, líneas y cantidades de elementos AST | Paso inicial automático obligatorio |
| `detectar_llamadas_sensibles` | Código; hasta 20 indicadores de llamadas como `eval`, `exec`, `os` y `subprocess` | Heurística AST sin ejecutar las llamadas |
| `revisar_consultas_sql` | Código; hasta 20 indicadores de SQL dinámico en `execute`/`executemany` | Heurística con posibles falsos positivos y omisiones |
| `ampliar_contexto` | Línea existente; hasta 13 líneas, radio 6 y hasta 500 caracteres por línea | Solo v2; conserva números y marca truncamiento |
| `buscar_referencia` | Categoría permitida; hasta 2 fragmentos de 2.000 caracteres y metadatos | Solo v2; consulta el índice local, no navega a URLs |
| `finalizar` | Sin argumentos; pasa a síntesis | Decisión de control, no herramienta ejecutada |

Categorías: `ejecucion_codigo`, `inyeccion_sql`, `inyeccion_comandos`, `inyeccion`,
`credenciales`, `rutas` y `deserializacion`. Cada una tiene una consulta fija. El esquema rechaza
argumentos ajenos a la herramienta, propiedades extra, líneas inválidas y
categorías no permitidas. No hay shell, consultas libres ni herramientas de
escritura. Ruff/Bandit son procesos autorizados de análisis; no ejecutan el
código del usuario como programa. Ruff selecciona deliberadamente `E4,E7,E9,F`; no representa todas sus reglas disponibles.

## Bucle de decisión y límites

1. Pydantic valida nombre `.py` sin rutas, texto de 1 a 12.000 caracteres y
   `max_pasos` de 1 a 4 para v2 (v1 y valor predeterminado conservan 3). Se rechazan código vacío y bytes NUL.
2. Ruff/Bandit producen evidencia y se ejecuta `inspeccionar_estructura` como paso 1.
3. Gemini recibe el código como datos no confiables y los resultados observados.
   Selecciona una herramienta autorizada con argumentos tipados o `finalizar`.
4. Backend valida y ejecuta la decisión. Su resultado alimenta la decisión
   siguiente. Repetir herramienta y argumentos detiene el bucle; argumentos
   diferentes consumen otro paso dentro del mismo límite.
5. Al finalizar, la síntesis Gemini + RAG recibe la evidencia efectivamente reunida.
   Las citas y ubicaciones se validan antes de publicarse.

En v2 hay hasta cuatro pasos totales, incluida la inspección inicial, hasta tres
decisiones y una síntesis. React conserva su petición explícita de tres pasos;
el laboratorio permite cuatro y el evaluador final los solicita por defecto. `max_pasos=1` evita decisiones adicionales, pero mantiene síntesis y
controles estáticos. La solicitud admite como máximo nueve intentos al proveedor,
incluidos reintentos, y un plazo cooperativo de hasta 150 segundos, reducible por
configuración. No es una promesa de latencia ni cancelación forzosa de tareas
locales. El frontend espera hasta 180 segundos; dejar de esperar no revoca lo iniciado.

La configuración centralizada está en [settings.py](../backend/app/config/settings.py).
Omitir `version_herramientas` conserva v1; React solicita explícitamente v2. El
contrato v2 permite el cuarto paso sin habilitar escritura ni aumentar el plazo o los nueve intentos.

## Evidencia, fuentes y trazabilidad

El planificador recibe un resumen de hasta 20 reglas estáticas. La evidencia de
síntesis admite hasta 40 reglas priorizadas por severidad y tres inspecciones con
hasta 20 indicadores cada una, además de los contextos y referencias v2. La
respuesta conserva la lista estática completa y sus estados. Resumen y respuesta
completa tienen límites diferentes.

Las referencias recuperadas por la herramienta v2 se reutilizan como contexto y
lista permitida de citas. Si no se recuperó ninguna, se conserva la recuperación
por categorías derivadas de evidencia. Se limita a seis fuentes únicas de seguridad;
los documentos de contexto del proyecto no se convierten en fuentes oficiales.
El [inventario](04-fuentes.md) contiene ocho originales y seis reglas curadas.

Cada hallazgo contextual aceptado cita IDs recuperados y un fragmento literal de
una sola línea. La línea declarada solo se ajusta si el fragmento tiene ubicación
única, conservando `linea_reportada_modelo`. Un fragmento ambiguo o cita inválida
descarta ese hallazgo. Si quedan hallazgos válidos, se conservan con estado parcial;
si todos se rechazan, el sistema se abstiene. Resolver un ID y encontrar un
fragmento no prueba pertinencia semántica ni explotabilidad.

La traza publica acciones observables, no razonamiento interno:

- `pasos`: herramienta, resultado, motivo público, origen `automatico`, `gemini`
  o `local`, y argumentos cuando corresponde en v2.
- `decisiones`: `ejecutada`, `finalizar`, `repetida` o `error`; un error no se muestra
  como resultado exitoso.
- `terminacion`: `finalizacion_anticipada`, `max_pasos` o `herramienta_repetida`.
- `fase_error`: `planificacion`, `herramienta`, `informe` o `null`.

La prioridad conserva la severidad original. La política integrada del PR #48 usa
pesos 8/4/2/1 y factores Bandit 1,0/0,8/0,6, con severidad dominante, desempate por
categoría y orden estable. Sin confianza reconocida no hay puntuación. La confianza
de Bandit no se atribuye a Gemini ni representa una probabilidad calibrada.
Véase la [política estática](10-analisis-estatico.md) y su
[validación conjunta](31-validacion-conjunta-pr46-pr47.md).

El candidato que incorpora el PR #54 añade la [política de severidad derivada](35-severidad-derivada-herencia.md):
Bandit alta × confianza alta deriva crítica conservando el original. El hallazgo
contextual debe citar IDs estáticos ofrecidos y coincidir con su línea validada.
Compartir ventana no autoriza herencia. Se conserva la severidad del modelo y
las reglas aplicadas en pantalla y JSON; un vínculo inválido se omite y marca
la revisión parcial. La matriz está en `backend/app/config/severidad.yaml`.
Esta implementación no demuestra por sí sola mejor detección ni explotabilidad.

## Respaldo, abstención y errores

`POST /api/v1/agente/previsualizar` ejecuta AST sin Gemini, con
`modo: "inspeccion_local"` e informe abstenido. Es distinto de previsualizar una
corrección o un presupuesto.

La ruta de análisis devuelve `modo: "gemini_real"` si planificación y síntesis
terminan sin error de proveedor, aunque el informe puede ser parcial o abstenido
por validación. Ese nombre de modo en un fixture no acredita una llamada real.
Ante errores controlados 502/503/504 conserva pasos, decisiones y evidencia
estática y responde HTTP 200, `modo: "degradado"`, estado parcial. Puede completar
AST local sin atribuirlo al modelo. Otros estados, como un 429 de la protección
HTTP, no se convierten automáticamente en éxito.

Se distinguen fallos de planificación, herramienta y síntesis. No se devuelven
claves ni mensajes crudos del proveedor. El respaldo puede agregar latencia y
no equivale a un dictamen completo. Ruff/Bandit tienen sus propios estados de
error o timeout, que la interfaz conserva.

## Confirmación humana: dos autorizaciones diferentes

El bucle es de solo lectura. `requiere_confirmacion_humana` en su respuesta no
sustituye los protocolos de propuestas y decisiones:

| Flujo | Antes de decidir | Aprobar | Rechazar o caducar |
|---|---|---|---|
| Presupuesto ZIP/GitHub | Archivos, análisis previstos, máximo de intentos incluidos reintentos, modelo, plazo cooperativo y vencimiento | Autoriza analizar la instantánea vinculada a sesión, ID y hash | No autoriza consumo de Gemini; servidor rechaza propuestas vencidas |
| Copia corregida | Código original y propuesta, con consentimiento inicialmente desmarcado | Autoriza descargar una copia del contenido revisado | Cancela o impide utilizar la propuesta; no genera una copia aprobada |

El presupuesto no estima dinero ni tokens. Preparar GitHub sí descarga contenidos,
pero no consulta Gemini. El plazo cooperativo mostrado es un límite operativo,
no una predicción de duración. Previsualizar una corrección puede involucrar al
proveedor para generar la propuesta: aprobar autoriza la descarga, no afirma
que no hubo consumo previo.

Presupuesto usa `/api/v1/proyectos/previsualizar/zip`,
`/api/v1/proyectos/previsualizar/github` y `/api/v1/proyectos/{id}/decision`.
Correcciones usa `/api/v1/correcciones/previsualizar` y
`/api/v1/correcciones/{id}/decision`. Ambos validan sesión y estado propios.
No se ejecuta código ni se sobrescriben originales. Caducidad, idempotencia y
conflictos se detallan en [presupuesto](28-presupuesto-proyectos.md) y
[confirmación de correcciones](23-integracion-confirmacion-qa.md).

En la revisión 8e66b2c el presupuesto público seguía desactivado. El candidato
de cierre lo activa conjuntamente en Docker y requiere verificar el despliegue.
La prueba de interfaz usa el fixture local existente,
con configuración temporal en el proceso de pruebas y proveedores simulados.
No constituye activación del servicio publicado.

## Evaluación y evidencia verificable

| Registro | Qué acredita | Qué no acredita |
|---|---|---|
| [Revisión frontend v2 del 6 de noviembre](29-revision-frontend-agente-presupuesto.md) | Recorrido, traza, exportación y presupuesto en casos controlados | Precisión de Gemini o despliegue actual |
| [Validación integrada PR #48](31-validacion-conjunta-pr46-pr47.md) | Compatibilidad y prioridad sobre su candidato | Comparación real final |
| [Cierre documental y presupuesto del 7 de noviembre](evidencias/semana-4/cierre-agente-presupuesto-20261107/README.md) | Aprobación/rechazo/caducidad en interfaz y concordancia documental | Consumo real ni activación pública del presupuesto |
| [Evaluación histórica PR #37](24-validacion-real-postmerge.md) | Corrida real del flujo directo en `caecd71` | Ventaja del agente v2 respecto al flujo directo |
| [Comparador de rutas](../eval/README.md) | Método sobre los mismos veinte casos, conservando errores/parciales | Resultados por la mera existencia del evaluador |

Christian coordina la comparación final con Gemini real. Hasta revisar sus
resultados no se afirma que el agente mejore precisión, recall o latencia.
Identificar commit, dataset/hash, corpus, modelo, configuración, rutas, reintentos,
errores y denominadores. Recuperación documental y detección son métricas
diferentes. Las pruebas específicas están incluidas en los totales, no se suman nuevamente.

## Consumo y evaluación del agente v2 actualizado

El PR #52 añade `X-Codeguard-Consumo-IA`, con intentos SDK, respuestas y tokens de
entrada/salida/total reportados por el proveedor. Los valores ausentes quedan
`null`; un intento sin respuesta impide conocer el total de tokens. Si no hubo
llamadas al SDK, los contadores son cero. No contiene prompts, código o claves y
no equivale a una factura. El evaluador conserva cobertura y sumas parciales
explícitas, incluso en HTTP de error. No deduce ahorro de la cantidad de pasos.

La comparación final solicita cuatro pasos por defecto y el A/B de seis casos
solicita herramientas v2. Ese A/B mide solo la primera decisión por condición,
incluidos sus argumentos y finalización inicial; no certifica la calidad del
informe completo. Las trazas de cuatro pasos y hasta tres resultados
contextuales llegan a la síntesis. Véase el [protocolo](27-protocolo-comparacion-rutas.md)
y el [detalle de consumo](33-agente-cuatro-pasos-consumo.md).

## Riesgos y limitaciones

- Prompt injection: código y documentos son datos no confiables; decisiones y
  herramientas se validan. Esto reduce superficie, no demuestra resistencia absoluta.
- Falsos positivos, omisiones y citas débiles: requieren revisión humana. Ninguna
  de las capas garantiza seguridad.
- Datos sensibles: el modo real envía código al proveedor. No cargar secretos ni
  repositorios privados. SQLite almacena contenido temporal de propuestas; purgarlo
  no garantiza borrado en respaldos del volumen.
- Coste y latencia: el límite de pasos no equivale al número de intentos. Cancelar
  la espera no revoca llamadas iniciadas.
- Cobertura y autonomía: solo Python y proyectos pequeños; sin memoria persistente
  de decisiones, ejecución del código, escritura autónoma ni streaming.
- Operación: concurrencia por proceso y almacenamiento compartido requieren
  revisión antes de múltiples réplicas. Una fusión no certifica despliegue.

## Código y reproducción

Fuentes: [orquestador](../backend/app/services/agente.py),
[rutas](../backend/app/routes/agente.py), [evidencia](../backend/app/services/evidencia.py),
[síntesis](../backend/app/services/llm.py), [interfaz](../frontend/src/pages/HomePage.tsx)
y [panel de traza](../frontend/src/components/AgentTracePanel.tsx).

```powershell
python -m pytest backend/tests/test_agente.py backend/tests/test_agente_integrado.py backend/tests/test_agente_herramientas_v2.py backend/tests/test_contrato_agente_v2.py -q
python qa/run_project_budget_browser.py --output tmp/presupuesto-validacion-nueva
```

El segundo comando requiere RAG local preparado y Playwright. Inicia servidores
de prueba en loopback y sustituye Gemini/GitHub; no apuntarlo a producción.
En `frontend/`: `npm test`, `npm run lint`, `npm run build`. Registrar resultado
y commit sin trasladar conteos históricos a una ejecución nueva.

## Cobertura documental tras la comparación real

La corrida real de 8e66b2c detectó que reutilizar exclusivamente las fuentes de
`buscar_referencia` podía perder una referencia pertinente que sí recuperaba el
flujo base del código. El candidato de cierre reserva las fuentes base y añade
las elegidas por el planificador, deduplicadas y con máximo seis. La herramienta
sigue influyendo en la síntesis y conserva su traza. No se alteran el dataset ni
las etiquetas. La corrida anterior se conserva; el ajuste requiere su propia
evaluación sobre la revisión desplegada.
