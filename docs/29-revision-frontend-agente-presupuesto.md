# Revisión de Ronald: agente v2 y presupuesto ZIP/GitHub

Responsable: Ronald Yépez, frontend y documentación. Fecha: 6 de noviembre de 2026.
Referencia común: `9c97ca1c8797bad5bdfdf227dba119b7839d32c7`, PR #45.
Rama: `docs/frontend-agente-v2-presupuesto`.

## Recorrido del agente

En modo API, código y .py solicitan `version_herramientas: "2"`. El panel muestra
inspección inicial, herramienta, motivo, origen y argumentos. Ampliar contexto
presenta líneas literales acotadas; buscar referencia presenta documento, sección,
ID y fragmento. Las direcciones documentales son texto, no enlaces activos.

Se distinguen decisiones fallidas de ejecuciones, respaldo local de elección del
modelo y finalización anticipada de cobertura completa. Repetir herramienta y
argumentos detiene inspecciones. Si falla una fase, se conserva evidencia y se
señala el estado incompleto. El JSON exportado conserva la traza validada.
No se ejecuta código recibido. V1 sigue siendo legible.

## Recorrido del presupuesto

Es **un límite de intentos al proveedor, incluidos reintentos**, no una estimación
de dinero ni tokens. ZIP/GitHub conservan análisis por archivo, fuera del agente v2.
Con la función desactivada se mantiene el flujo anterior.

1. «Revisar presupuesto» prepara una instantánea sin Gemini. GitHub sí se consulta
   para obtener contenidos. La vista muestra archivos, caracteres, modelo, análisis
   previstos, máximo de intentos, plazo cooperativo y vencimiento.
2. La casilla comienza desmarcada. Aprobar envía ID, hash, decisión y consentimiento;
   el navegador no impone un presupuesto distinto al del servidor.
3. Rechazar o cambiar entrada antes de aprobar no autoriza consumo. Cambiar entrada
   solicita rechazo de la propuesta previa; si falla, esta permanece hasta caducar.
4. Aprobar autoriza solo la instantánea preparada. El cliente valida identidad,
   hash, nombres y cantidad del resultado. Repetir una aprobación finalizada
   recupera el resultado sin nuevas llamadas.
5. «Dejar de esperar», después de aprobar, solo interrumpe la espera del navegador.
   No revoca llamadas iniciadas ni promete detener tareas locales en curso.
6. Caducidad o conflicto requieren revisar el estado antes de otro análisis.
   Se corrigió el encabezado «Integración pendiente» por «Solicitud no completada».

Hasta cinco Python, 12.000 caracteres combinados y ZIP de hasta 5 MB. Máximo de
intentos: `min(archivos × intentos configurados, 15)`, hasta tres por archivo.
Plazo cooperativo máximo 150 s. Propuesta pendiente: 300 s. El panel muestra los
valores efectivos devueltos por Backend. El [contrato](28-presupuesto-proyectos.md)
detalla sesiones, persistencia y HTTP 404/409/410/422/428/429.

Aprobar presupuesto autoriza **analizar**. La confirmación de correcciones autoriza
**descargar una copia**. Son operaciones independientes.

## Trazabilidad

| Observación/requisito | Cambio o componente | Verificación | Límite |
|---|---|---|---|
| Contexto y referencias visibles | `AgentTracePanel`, parser `agentTrace`, solicitud v2 | `agent-v2.test.tsx`; navegador caso completo | La propagación al planificador y síntesis usa Gemini simulado |
| Finalización comprensible | Terminación y decisiones | Navegador: anticipada y repetición | No certifica ausencia de vulnerabilidades |
| Error sin resultado inventado | Fase incompleta y respaldo local | Navegador: error contextual | Backend real, proveedor simulado |
| Exportación de procedencia | `createReport` conserva traza | `agent-v2.test.tsx` | Contrato/exportación, no pertinencia semántica |
| Presupuesto antes de consumo | `ProjectBudgetReview`, `projectBudget`, `HomePage` | Navegador: previsualización, aprobación GitHub y ZIP | Previsualizar/rechazar no llama a Gemini |
| Consentimiento vinculado a entrada | Casilla, ID, hash y cambio de entrada | Navegador: cambio, rechazo, idempotencia y hash alterado | Sesión/SQLite reales, Gemini/GitHub simulados |
| Vencimiento comprensible | Error 410 y encabezado corregido | Navegador: caducidad y ausencia del rótulo anterior | No equivale a integración pendiente |
| Vista móvil | Paneles de agente y presupuesto | Navegador a 390 px, capturas | Revisión visual local |
| Severidad × confianza | Propuesta y fórmula a cargo de Backend | Pendiente de sus reglas y pruebas | El orden actual por severidad/categoría no cubre ese requisito |
| Comparación real de veinte casos | Coordinación de Christian | Pendiente de resultados finales | Los resultados de caecd71 no se atribuyen a v2 |

Ejecutores: [agente](../qa/run_agent_v2_browser.py),
[presupuesto](../qa/run_project_budget_browser.py),
[contrato/exportación](../frontend/tests/agent-v2.test.tsx) y
[contrato presupuesto](../frontend/tests/project-budget.test.tsx).
Evidencia propia: [revisión frontend](evidencias/semana-4/revision-ronald-v2-presupuesto-20261106/README.md).
Las cifras del candidato previo conservan su autoría y commit en
[la evidencia original](evidencias/semana-4/integracion-agente-presupuesto-20261106/README.md).

## Presentación y coordinación

La [presentación](presentacion/README.md) mantiene doce minutos e incorpora v2,
presupuesto y límites. Recupera el trabajo del PR #39 como base y lo actualiza:
revisar esa dependencia para evitar duplicar cambios. La corrida real del PR #37
sobre caecd71 queda como histórica. Christian incorporará la comparación final
cuando disponga de resultados y commit identificados.

No se cambian `.env`, flags predeterminados, workflows, servicios backend ni
Railway. Los runners existentes habilitan lo necesario solo en procesos fixture
aislados con proveedores simulados. No se fusiona ni despliega. La integración
del PR #45 no demuestra qué revisión está activa en Railway.
