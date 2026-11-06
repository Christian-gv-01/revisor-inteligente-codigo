# Candidato integrado: agente v2 y consentimiento de proyectos

Commit probado con checkout limpio:
[`0cdaba0263c577445fab0daaec9e3dce7b2046d9`](https://github.com/Christian-gv-01/revisor-inteligente-codigo/commit/0cdaba0263c577445fab0daaec9e3dce7b2046d9).
Rama `codex/integracion-agente-presupuesto`. El commit documental posterior solo
adjunta estas evidencias, completa el plan y añade el índice; no cambia código,
tests, QA, workflows ni evaluador. [Procedencia, árboles y hashes](procedencia.json).

Ambos candidatos son ancestros: PR43 `f2dbfa38` y PR44 `f2935f2`, base común
`605d142`. Sin conflictos de Git ni integración a main. Los originales quedan
abiertos en borrador; la rama nueva permite revisar el conjunto.

## Compatibilidad

| Área | Resultado |
|---|---|
| Agente PR43 | Código/Python solicita v2; v1 sigue legible; herramientas y límites conservados |
| Presupuesto PR44 | ZIP/GitHub conservan consentimiento, snapshot, rechazo sin consumo e idempotencia |
| Rutas y consumo | Proyectos mantienen análisis por archivo; no se mandan al agente ni aumentan su presupuesto |
| Frontend | Argumentos, resultados, procedencia y terminación visibles y exportables; valida ventanas literales, categorías, documentos y correspondencia decisiones/pasos |
| Fallos | Decisión fallida sin resultado inventado; respaldo local y fase incompleta diferenciados |
| Datos no confiables | Texto escapado por React; documentos sin enlaces activos. No se ejecuta código recibido |
| Límites PR42 | Tres pasos, dos decisiones, una síntesis, nueve intentos y plazo cooperativo de 150 s conservados |
| Configuración | Presupuesto apagado por defecto; sin cambios en Railway ni despliegues |
| Fuera de alcance | Priorización y evaluador sin modificaciones |

Se corrigió una incompatibilidad en los ejemplos sintéticos del PR43: declaraban
análisis estático completo con `herramientas: []`. El generador y cuatro respuestas
ahora representan los estados de Ruff/Bandit simulados. Se mantuvo la validación
del frontend que exige estados de los motores.

## Pruebas del mismo commit

| Comprobación | Resultado |
|---|---|
| Backend | **495 aprobadas**, [JUnit](backend-junit.xml) |
| Frontend | **132 aprobadas**, 24 HTTP omitidas sin servidor; [JUnit](frontend-junit.xml) |
| Lint / build | Aprobados; advertencia previa de bundle mayor de 500 kB |
| QA/eval existente | **23 aprobadas**, una omitida por enlaces simbólicos en Windows; [JUnit](qa-eval-junit.xml) |
| Agent Lab | Comprobación JS/ejemplos/traza aprobada |
| HTTP con Ruff/Bandit reales | **24 aprobadas**, [resultado](http-estatico.json) |
| HTTP sin análisis estático | **19 aprobadas**, cinco omitidas por requerir estático; [resultado](http-sin-estatico.json) |
| Navegador agente v2 | **6 escenarios aprobados**, [casos](navegador-agente-v2.json), [log](navegador-agente-v2.txt) |
| Navegador presupuesto | **9 escenarios aprobados**, [casos](navegador-presupuesto.json), [log](navegador-presupuesto.txt) |
| Revisión independiente | Sin bloqueantes; 46 pruebas frontend y 131 backend focalizadas aprobadas |

Chrome local mediante Playwright aislado; Vite en loopback, FastAPI/orquestador,
SQLite/ChromaDB/Ruff/Bandit reales. SDK Gemini y transporte GitHub simulados.
Los flags se habilitan solo dentro del proceso fixture del presupuesto. Cero
llamadas externas de IA. No son métricas de calidad ni resultados de Gemini real.

Los escenarios v2 prueban propagación real al siguiente prompt y síntesis, móvil
sin desbordamiento, finalización con una decisión y una síntesis, repetición sin
otra inspección, error con respaldo y ausencia de errores/red externa del
navegador. Respuestas: [completa](respuesta-v2-full.json),
[anticipada](respuesta-v2-early.json), [repetición](respuesta-v2-repeat.json),
[error](respuesta-v2-error.json).

Los nueve escenarios del presupuesto conservan el runner PR44 y prueban
previsualización, consentimiento desmarcado, rechazo sin consumo, móvil,
aprobación, idempotencia, cambio de entrada, caducidad, ZIP de dos archivos y hash
alterado; algunos se agrupan en un escenario.

## Reproducción y capturas

Con dependencias y corpus ingerido, ejecutar `pytest tests -q` dentro de backend,
`pytest qa eval -q` en raíz, `npm test`, `npm run lint` y `npm run build` en
frontend. Desde raíz ejecutar `eval/run_integration.py` con/sin `--static-analysis`
y `qa/run_agent_v2_browser.py` / `qa/run_project_budget_browser.py`, siempre con
`--output` en carpetas nuevas. Usar el Python del entorno backend.

Los runners navegador requieren `PLAYWRIGHT_MODULE_PATH`; `CODEGUARD_BROWSER_PATH`
permite Chrome local. CI instala Chromium y adjunta JSON, logs y capturas de
ambos runners en `integracion-http`. Capturas locales del commit probado:
`tmp/http-publicado-agente-v2/agente-v2-escritorio.png`, `agente-v2-movil.png` y
`tmp/http-publicado-presupuesto/presupuesto-escritorio.png`, `presupuesto-movil.png`.
No se publican SQLite ni ZIP temporales.

Entrega para revisión, sin activar funciones públicas, fusionar ni desplegar.
