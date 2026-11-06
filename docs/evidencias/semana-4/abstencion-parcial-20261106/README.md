# Verificación local — abstención y conservación parcial

6 de noviembre de 2026, Windows, Python 3.13.7. Base Git `b7431c1`, con
los cambios locales de `codex/abstencion-hallazgos` aplicados. Estos resultados
no se atribuyen a GitHub Actions ni al despliegue público.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Regresiones antes del cambio | 21 fallos, 6 aprobadas | Ejecución TDD de `tests/test_abstencion_parcial.py`; salida observada durante la sesión, sin log versionado |
| Backend final | 316 aprobadas, 0 fallos | [JUnit](backend.xml), incluye 30 casos nuevos |
| QA y evaluador | 23 aprobadas, 1 omitida, 0 fallos | [JUnit](qa-eval.xml); el equipo Windows no permite crear el enlace simbólico del test de empaquetado |
| Frontend unitario | 91 aprobadas, 24 omitidas | `npm test -- --reporter=dot`; las omitidas corresponden a HTTP y se ejecutaron por separado |
| Frontend ESLint | Aprobado | `npm run lint`, código de salida 0 |
| Frontend TypeScript/Vite | Aprobado | `npm run build`, código de salida 0; advertencia conocida de bundle >500 kB |
| Agent Lab | JavaScript y controles correctos | `node qa/check_agent_lab_ui.cjs`, código de salida 0 |
| HTTP con Ruff/Bandit | 24/24 aprobadas | [Reporte](http-estatico.json) |
| HTTP sin estático opcional | 19 aprobadas, 5 no aplicables | [Reporte](http-sin-estatico.json) |
| Revisión independiente | Sin bloqueos; 116 pruebas relevantes aprobadas por el revisor | Revisión del diff, sin cambios de implementación del revisor |

Los dos reportes HTTP usan ChromaDB local real; Gemini y la descarga externa de
GitHub están simulados. No consumen llamadas externas de IA. Los timeouts del
log son casos controlados de respaldo, no incidencias del proveedor real.

La suite nueva prueba código, .py, ZIP, GitHub y agente por HTTP. Cubre
abstención con/sin motivo, estados contradictorios, citas ausentes/inventadas,
deduplicación, compatibilidad directa sin fragmento y lotes con omisión documental
seguida de timeout. Las pruebas previas conservan el anclaje obligatorio del agente.

Los reportes JSON incluyen hashes de procedencia y la configuración del entorno
fixture. JUnit permite verificar los conteos finales. No se guardaron credenciales
privadas ni se incluyó el PDF original del docente en el repositorio.

## Reproducción

Desde `backend/`: `.\.venv\Scripts\python.exe -m pytest tests -q`.
Desde la raíz: `backend\.venv\Scripts\python.exe -m pytest qa eval -q`.
Desde `frontend/`: `npm test`, `npm run lint`, `npm run build`.
Desde la raíz:

```powershell
backend\.venv\Scripts\python.exe eval/run_integration.py --static-analysis --output tmp/abstencion-http-estatico-nuevo
backend\.venv\Scripts\python.exe eval/run_integration.py --output tmp/abstencion-http-sin-estatico-nuevo
```

Usar directorios nuevos. No se midieron precisión/recall/F1 de Gemini ni se
realizó despliegue; los pendientes restantes están en [la documentación del cambio](../../../26-abstencion-parcial.md).
