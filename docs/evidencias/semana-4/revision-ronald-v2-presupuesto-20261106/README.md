# Revisión frontend de Ronald sobre agente v2 y presupuesto

Fecha: 6 de noviembre de 2026. Base acordada `9c97ca1`.
Código revisado: `ecfa1a6219086132a60d3d6e5707c794e99521c6`.
La prueba precedió al commit y sus bytes se contrastaron con Git después;
[procedencia y hashes](procedencia.json). Los cambios documentales posteriores
no modifican los componentes ni los ejecutores probados.

| Comprobación propia | Resultado |
|---|---|
| Unitarias frontend | 132 aprobadas, 24 HTTP omitidas sin servidor en esa suite |
| ESLint / build | Correctos; advertencia previa de bundle mayor de 500 kB |
| Agente v2 desde HomePage | Seis escenarios aprobados |
| Presupuesto GitHub/ZIP | Nueve escenarios aprobados |
| Revisión visual | Escritorio y móvil 390 px, traza y consentimiento legibles |

Resultados originales: [agente](navegador-agente-v2.json),
[presupuesto](navegador-presupuesto.json), [unitarias](frontend-tests.txt) y
[build](frontend-build.txt).

Capturas: [agente escritorio](agente-v2-escritorio.png),
[agente móvil](agente-v2-movil.png),
[presupuesto escritorio](presupuesto-escritorio.png) y
[presupuesto móvil](presupuesto-movil.png).

Las etiquetas «API real» y «Elegido por Gemini» pertenecen al contrato de la
aplicación. En estas capturas el proveedor es **simulado**, como indican las
respuestas fixture. No son evidencias de Gemini real ni capturas de producción.

## Qué se comprobó

Agente: argumentos y resultados contextuales, propagación a decisión/síntesis,
finalización anticipada, repetición, error contextual sin resultado inventado y
ausencia de errores JavaScript/red externa. Incluye móvil.

Presupuesto: previsualización sin Gemini, casilla desmarcada, rechazo sin consumo,
aprobación, idempotencia, nueva entrada, caducidad 410, ZIP con dos archivos y
manifiesto alterado 409. Incluye móvil. La comprobación de caducidad exige el nuevo
encabezado «Solicitud no completada» y rechaza el anterior «Integración pendiente».

Los totales son escenarios agrupados, no llamadas al proveedor. Las llamadas
simuladas se cuentan para comprobar consentimiento e idempotencia.

## Reproducción

Desde frontend: `npm ci`, `npm test -- --reporter=dot`, `npm run lint`, `npm run build`.
Desde la raíz, con dependencias backend y modelo local preparados:

```powershell
python scripts/ingest.py
python qa/run_agent_v2_browser.py --output tmp/revision-agente-nueva
python qa/run_project_budget_browser.py --output tmp/revision-presupuesto-nueva
```

Playwright debe estar disponible; `PLAYWRIGHT_MODULE_PATH` permite indicar su
`index.mjs`, y `CODEGUARD_BROWSER_PATH` un navegador aislado de pruebas. Se usó
Edge headless, Vite/FastAPI en loopback y SQLite temporal. Los runners existentes
activan sus flags solo dentro del fixture; no se editó configuración persistente.
GitHub/Gemini están sustituidos, RAG y analizadores son reales.

Los primeros intentos bajo sandbox no iniciaron el servidor fixture y no se
cuentan como aprobados. Las corridas registradas se completaron con acceso local
al servidor y navegador. No se publican las bases SQLite ni ZIP temporales.

No se repitió la suite completa de Backend, la comparación generativa ni la
verificación de Railway. Esas tareas pertenecen al cierre coordinado de Backend
y Christian. Los resultados anteriores conservan su commit y no se suman a estos.
