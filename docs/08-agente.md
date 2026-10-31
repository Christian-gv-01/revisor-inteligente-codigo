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

## Confirmación humana

No se permite modificar, ejecutar o borrar código, por lo que **no hay decisiones destructivas que autorizar**. Toda corrección sugerida debe ser evaluada y aplicada por un humano. Si se añaden herramientas que cambien archivos, requerirán consentimiento explícito antes de ejecutarse.

## Pruebas

`backend/tests/test_agente.py` cubre validaciones, seguridad, límites, heurísticas AST, elección de herramientas, interrupción, y endpoints HTTP con mocks. Ejecutar en la versión integrada y registrar el conteo exacto de pruebas. No se documentan como resultados reales las comprobaciones no ejecutadas.

## Limitaciones

No hay memoria persistente, ejecución autónoma, modificaciones del repositorio ni streaming real de decisiones. La traza se muestra **al finalizar** cada solicitud; la animación de espera no representa actividad intermedia verificada. Las herramientas AST no son exhaustivas y pueden generar indicadores falsos o no detectar riesgos. Ante fallos de Gemini, el análisis real devuelve un error controlado y no se sustituye silenciosamente por resultados locales.
