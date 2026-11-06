# Verificación local: reintentos, plazo y cupos

6 de noviembre de 2026, Windows y Python 3.13.7. Base `2cb3e82`, con cambios
locales de `codex/reintentos-presupuesto`. No se atribuyen estas ejecuciones a CI.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Backend | 364 aprobadas, 0 fallos | [JUnit](backend.xml), incluye 48 casos nuevos |
| QA y evaluador | 23 aprobadas, 1 omitida | [JUnit](qa-eval.xml); enlace simbólico no permitido en este equipo |
| Frontend | 91 aprobadas, 24 HTTP omitidas en la suite unitaria | npm test; HTTP se ejecuta por separado |
| ESLint y TypeScript/Vite | Aprobados | npm run lint/build; persiste advertencia de bundle >500 kB |
| Agent Lab | Aprobado | node qa/check_agent_lab_ui.cjs |
| HTTP con estático | 24/24 | [Reporte final](http-estatico-final.json) |
| HTTP sin estático opcional | 19 aprobadas, 5 no aplicables | [Reporte final](http-sin-estatico-final.json) |
| Revisión independiente de reservas | Sin bloqueos, 27 pruebas focalizadas aprobadas | SQLite, fallo, hilos/proceso y recuperación |
| Revisión independiente general | Sin bloqueos pendientes, 34 pruebas de presupuesto/HTTP aprobadas | Retorno prematuro RAG reproducido y corregido |
| Política de severidad/modelos públicos | Sin cambios frente a base | git diff --quiet sobre modelos y dos archivos de priorización |

Regresiones de reserva antes del cambio: ocho fallos y una aprobada. El módulo
de presupuesto se especificó con pruebas antes de crearlo; la primera ejecución
falló al importar el módulo todavía ausente. Las pruebas posteriores comprueban
conducta con reloj y sueño simulados, no esperas reales ni consumo de IA.

El SDK google-genai real se verifica con HTTPX MockTransport: primer transporte
429, espera de un segundo, segundo transporte correcto y timeout reducido de
cinco a cuatro segundos. Se comprueba que el SDK no multiplica los intentos.

Los casos HTTP distinguen 429 propio sin generación de 429 del proveedor agotado
en 503; validan plazo consumido por RAG, aislamiento entre solicitudes, estado
parcial con estático, traza conservada del agente y reserva liberada al vencer.
El test de proceso hijo usa spawn y el mismo archivo SQLite: el padre no consigue
el último cupo mientras genera el hijo, sin depender de un bloqueo en memoria.

La primera CI del PR42 detectó dependencia accidental del motor estático en
HTTPX/SDK, ausentes del workflow mínimo ([corrida](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42300854663)).
Se añadió una regresión en proceso nuevo que bloquea esas importaciones, falló
antes de corregirlas y aprobó después: excepción de plazo estándar e importación
del SDK solo al generar. Los reportes http-estatico.json/http-sin-estatico.json
conservan la primera ejecución previa a ese ajuste; los enlaces finales registran
la repetición con el código corregido. El JUnit inicial de 363 casos se conserva
en el commit 9d07600, antes de añadir la nueva regresión.

Las pruebas de RAG/integración usan ChromaDB real; Ruff/Bandit son reales cuando
están activados. Gemini y la API externa GitHub son simulados. Los informes
incluyen hashes de procedencia. No contienen credenciales privadas.

## Reproducción

Desde backend: `.\.venv\Scripts\python.exe -m pytest tests -q`.
Desde raíz: `backend\.venv\Scripts\python.exe -m pytest qa eval -q`.
Desde frontend: `npm test`, `npm run lint`, `npm run build`.
Desde raíz, con carpetas nuevas:

```powershell
backend\.venv\Scripts\python.exe eval/run_integration.py --static-analysis --output tmp/reintentos-http-estatico-nuevo
backend\.venv\Scripts\python.exe eval/run_integration.py --output tmp/reintentos-http-sin-estatico-nuevo
```

[Base main/Railway verificada](main-validado.json). [Comportamiento y límites](../../../reintentos-presupuesto.md).
El plazo es cooperativo; esta evidencia no certifica un tiempo máximo absoluto
del servicio público ni mide precisión/recall/F1 del modelo.
