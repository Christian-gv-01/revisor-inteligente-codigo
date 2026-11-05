# 08 — Agente supervisado CODEGUARD (Agent Mission Control)

## Propósito

Ampliar el revisor de seguridad con una **capa de orquestación limitada** y una trazabilidad observable de herramientas. El objetivo es demostrar un agente que observa la estructura del código, escoge herramientas autorizadas y entrega al usuario los resultados **sin ejecutar código no confiable**.

## Arquitectura y decisiones

1. `POST /api/v1/agente/analizar` valida la entrada por `SolicitudAgente` (Pydantic).
2. `inspeccionar_estructura` ejecuta siempre una inspección AST inicial.
3. **Gemini** selecciona una herramienta adicional de la lista cerrada o finaliza. Su decisión se valida por `DecisionAgente`; recibe resultados reales de herramientas previas para planear la siguiente acción.
4. Cada herramienta es determinista y sin efectos secundarios: `inspeccionar_estructura`, `detectar_llamadas_sensibles`, `revisar_consultas_sql`.
5. El orquestador limita el flujo a **máximo 3 pasos**, corta decisiones repetidas y prohíbe comandos arbitrarios.
6. Al terminar, el informe definitivo viene del analizador `analizar_codigo` existente, que usa Gemini y fuentes RAG verificables. **Las observaciones AST son indicadores auxiliares; no equivalen automáticamente a hallazgos confirmados**.
7. `GET /agente/demo` muestra el trazado público de las herramientas, el dictamen y las fuentes documentales.

El modo local `POST /api/v1/agente/previsualizar` ejecuta únicamente las herramientas AST y devuelve una abstención explicando que no hubo IA. Sirve como demostración segura si el proveedor externo no está disponible, pero **no debe presentarse como un análisis con Gemini**.

## Contrato Pydantic y límites

`SolicitudAgente`: `archivo` .py válido sin ruta, `codigo` de 1 a 12000 caracteres, `max_pasos` entre 1 y 3. También se rechaza texto vacío o binario con NUL.

`DecisionAgente`: tipo literal de herramienta y motivo breve (texto descriptivo publicable, no cadena de razonamiento oculta).

`RespuestaAgente`: archivo, modo real o local, pasos detallados, límite, informe estructurado, política de seguridad y campo de confirmación humana. 

## Degradación controlada cuando falla Gemini (Semana 4)

- El modo normal devuelve `modo=gemini_real` únicamente cuando el planificador y el informe contextual Gemini + RAG terminan correctamente.
- Cuando Gemini devuelve un error del proveedor HTTP **502, 503 o 504**, el endpoint `/api/v1/agente/analizar` ejecuta de nuevo las herramientas AST locales autorizadas, respeta `max_pasos` y entrega HTTP 200 **con `modo=degradado`, `informe.estado=parcial`**, sin hallazgos de IA ni fuentes RAG inventadas.
- Este modo degradado **no equivale a un dictamen de seguridad**: los indicadores AST pueden ser incompletos o imprecisos. La interfaz debe informar de ello y no presentar la ejecución como «auditoría con IA finalizada».
- Otros errores (por ejemplo un 429 de la capa HTTP) conservan su estado original, en vez de ocultarse bajo un resultado parcial.
- Los errores del planificador se diferencian: 408/504 → 504; saturación 429/500/502/503 → 503; respuesta inválida o decisión no autorizada → 502. Los detalles internos, la clave API y los mensajes crudos del proveedor **no** se muestran al usuario.
- Se conserva una lista cerrada de herramientas de solo lectura y un máximo de tres pasos. No se ejecuta, importa o modifica el código de entrada.

**Limitación:** el fallback se realiza después de que fallen las consultas a Gemini; por lo tanto puede haber latencia adicional. No se ha demostrado un 503 real en Railway con fallback hasta ejecutar una prueba de aceptación en producción. Las pruebas de regresión simulan al proveedor y verifican el contrato seguro.

## Confirmación humana

No se permite modificar, ejecutar o borrar código, por lo que **no hay decisiones destructivas que autorizar**. Toda corrección sugerida debe ser evaluada y aplicada por un humano. Si se añaden herramientas que cambien archivos, requerirán consentimiento explícito antes de ejecutarse.

## Pruebas

`backend/tests/test_agente.py` cubre validaciones, seguridad, límites, heurísticas AST, elección de herramientas, interrupción, y endpoints HTTP con mocks. Ejecutar en la versión integrada y registrar el conteo exacto de pruebas. No se documentan como resultados reales las comprobaciones no ejecutadas.

## Limitaciones

No hay memoria persistente, ejecución autónoma, modificaciones del repositorio ni streaming real de decisiones. La traza se muestra **al finalizar** cada solicitud; la animación de espera no representa actividad intermedia verificada. Las herramientas AST no son exhaustivas y pueden generar indicadores falsos o no detectar riesgos. Ante fallos transitorios de Gemini, la ruta del agente informa explícitamente un resultado **degradado y parcial**, sin atribuir la inspección AST a Gemini. El análisis no implica seguridad garantizada.
