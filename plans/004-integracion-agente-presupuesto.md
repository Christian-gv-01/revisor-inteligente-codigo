# Candidato de integración PR43 + PR44

Base común: `605d142ff8f643d755689e257c649e0a9e79a8ea`.
PR43: `f2dbfa38dd0c5325bc84cdebd57d26a3c297e51c`.
PR44: `f2935f2b306bf0130c6051bff7df0a985f3436f1`.
Rama: `codex/integracion-agente-presupuesto`, worktree administrado aparte.

## Diseño y alcance autorizado

Integrar las dos ramas con historia conservada y adaptar el frontend existente.
La integración de Git no presentó conflictos. PR43 cambia agente/evidencia/LLM;
PR44 añade rutas, sesión y snapshot de proyecto. Comparten límites globales del
PR42 sin aumentar pasos, llamadas o plazo. Los proyectos conservan su contrato
por archivo y su consentimiento, no se redirigen al agente.

Se elige ampliar tipos/parser/panel frente a renderizar JSON crudo (pierde
validación y semántica) o rediseñar el flujo completo (fuera del alcance).
El servicio de código/Python solicita v2; el parser también acepta v1. Ventanas,
documentos y AST tienen formas discriminadas, argumentos tipados y topes. El
panel muestra resultado, procedencia, errores y finalización sin atribuir un
resultado a decisiones fallidas. React muestra texto escapado; no ejecuta código
ni abre URLs arbitrarias. Los datos exportados conservan la traza normalizada.

No modificar priorización ni evaluador. No activar flags en configuraciones de
producción, fusionar a main o desplegar. Presupuesto sigue apagado por defecto;
se activa solo dentro del proceso fixture de QA autorizado.

## Ejecución y verificación

- [x] Leer contratos, verificar SHAs, integrar ambos en worktree aislado.
- [ ] Confirmar baseline backend/frontend integrado antes de adaptar.
- [ ] Escribir pruebas frontend que fallen con ejemplos reales del PR43:
  contexto/referencias/argumentos, finalización, errores, v1 y exportación.
- [ ] Implementar tipos, validación estricta de resultados/argumentos y panel.
  Probar rechazo de categorías/URLs/ventanas inválidas y repetición por argumentos.
- [ ] Añadir prueba de navegador contra FastAPI real/orquestador real con SDK
  simulado para v2; conservar y ejecutar los nueve escenarios de presupuesto.
- [ ] Ejecutar backend, frontend tests/lint/build, QA/eval sin cambios e HTTP con
  y sin análisis estático en el mismo candidato. Cero Gemini externo.
- [ ] Fijar commit candidato, verificar checkout limpio, registrar JUnit,
  resultados/capturas y hashes/procedencia. Publicar rama/PR borrador de revisión.

Archivos nuevos: parser de traza `frontend/src/services/agentTrace.ts`, pruebas
`frontend/tests/agent-v2.test.tsx`, navegador `frontend/tests/agent-v2-browser.mjs`
y runner `qa/run_agent_v2_browser.py`. Adaptar `analysis.ts`, `api.ts`,
`AgentTracePanel.tsx/.css` y expectativa de request del test v1 existente.
Agregar CI del runner a workflow de integración sin tocar evaluador.

Comandos: Python del entorno backend existente contra este worktree; `pytest
tests -q`, `pytest qa eval -q`; `npm test`, `npm run lint`, `npm run build`;
`eval/run_integration.py` con/sin `--static-analysis`; runners navegador QA en
loopback con SQLite temporal y transporte externo simulado. Registrar límites
y omisiones: no son métricas de calidad de Gemini.
