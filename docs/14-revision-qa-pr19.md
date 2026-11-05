# Revisión QA del PR #19 y correcciones propuestas

Fecha: 5 de noviembre de 2026, America/Bogota. Responsable: `0123445-20Alexis`.

Propuesta publicada: [PR #23](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/23), en borrador sobre la rama del PR #19. Deben revisarse estos ajustes antes de consolidar la candidata.

Se revisó el PR #19 en `d85517ba5ad8d88be0f8f1bd66c861e47794afea`, sobre `integration/semana4-candidata` en `7f0ac9c6615d859162cb919ac1a884e3d117d261`. El trabajo se aisló en `feature/entrega4-qa-pr19`, partiendo del PR. No se fusionó a main, no se modificó la rama del compañero y no se desplegó Railway.

## Dictamen

El PR implementa la separación estático/RAG y el estado parcial, pero la revisión encontró dos defectos reproducibles. Se proponen sus correcciones y pruebas antes de aceptar la integración definitiva. La aceptación de esta propuesta se limita al candidato local y CI; no certifica Gemini real, GitHub público ni persistencia remota.

| Hallazgo | Reproducción | Corrección propuesta |
|---|---|---|
| QA19-01 — Se rechazan alertas válidas | `eval(user_input)` repetido 101 veces produce 101 alertas Ruff y 101 Bandit reales. React rechazaba las 202 porque su límite combinado era 200 | Alinear el máximo combinado a 400, dado el límite de 200 por motor. Probar 202 por HTTP y la frontera 400/402 |
| QA19-02 — Mensaje global de ausencia de problemas con alertas estáticas | `estado=analizado`, cero hallazgos Gemini y alertas B307/F821 muestra «No se encontraron hallazgos» | Diferenciar ausencia de hallazgos contextuales y observaciones/ejecuciones estáticas incompletas; añadir regresiones para error, timeout y herramienta ausente |
| QA19-03 — Prueba HTTP anterior al contrato resiliente | Con estático activado, la suite original obtuvo 8/9; esperaba 504 donde el candidato ahora devuelve 200/parcial | Probar ambos contratos explícitamente: parcial con respaldo estático y 504 con bandera apagada |
| QA19-04 — Aviso de privacidad aún no integrado | `feature/frontend-semana4` contiene el aviso, pero HomePage del candidato no | Integrar el texto aportado por el compañero mediante `PrivacyNotice`, visible únicamente en modo API, sin reemplazar toda la página |

## Resultados propios

| Comprobación | Resultado y alcance |
|---|---|
| PR #19 original, suite habitual | 65 aprobadas; 9 HTTP omitidas intencionalmente sin servidor |
| Regresiones QA antes de corregir | Dos fallos reproducidos; `regresiones-antes.json` |
| Suite habitual corregida | 71 aprobadas; 15 HTTP omitidas en esta invocación y ejecutadas por separado |
| HTTP con estático activado | 15/15 aprobadas: código, Python multipart, ZIP, GitHub controlado, estados parciales, referencias, renderizado y exportación, 202 alertas reales |
| HTTP con estático desactivado | 10/10 aplicables aprobadas; cinco casos exclusivos del motor estático omitidos |
| ESLint y build | Aprobados tras actualizar minimatch; persiste la advertencia histórica del tamaño del paquete Monaco |
| Auditoría npm original | 10 avisos moderados en dependencias de desarrollo |
| Auditoría tras corrección | 0 avisos totales y 0 al omitir dependencias de desarrollo; es una fotografía de la base de advisories consultada |
| Navegador, build compilado | Flujo GitHub parcial: dos archivos, cuatro observaciones, motores separados, aviso de privacidad y JSON descargado con B307/F821; revisado a 1440 y 390 px sin desbordamiento horizontal |

Entorno local: Windows, Python 3.12.14, FastAPI 0.156.1, ChromaDB 1.5.9, Ruff 0.14.1 y Bandit 1.8.6. Los endpoints y el cliente frontend realizan HTTP real en loopback. Gemini se sustituye por respuestas controladas; la API externa de GitHub se sustituye por `httpx.MockTransport`, conservando el lector y validador real del backend. No se consumió cuota Gemini ni se descargó un repositorio externo durante estas pruebas. Los fallos de Gemini son inducidos, no incidentes reales del proveedor.

Las capturas y `exportacion-ui.json` corresponden al build con estas correcciones sobre un servidor local de prueba. Aunque la interfaz diga «API real» y el JSON diga `backend`, el proveedor IA y la API GitHub son fixtures. El resto de modalidades se verificó por HTTP y renderizado de componentes, no se presenta como recorrido manual completo en navegador.

## Dependencias

La vulnerabilidad [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249) afecta a minimatch desde 7.0.0 hasta antes de 11.0.1. El lockfile original usa 10.2.6. Las versiones consultadas de ESLint todavía dependen de la rama 10, por lo que una actualización menor ordinaria no elimina el aviso.

Se propone un override explícito a `minimatch: 11.0.1`, regenerando el lockfile sin `npm audit fix --force`. ESLint 10.13.0 y TypeScript ESLint 8.72.0 permanecen iguales. Esto cambia la versión mayor de una dependencia transitiva: la compatibilidad se comprobó para este repositorio mediante instalación limpia, lint, build y tests; no se afirma compatibilidad universal para otros consumidores. Revisar y retirar el override cuando los paquetes consumidores incorporen una versión corregida compatible en su propio rango.

## Coordinación con Frontend

La rama remota `feature/frontend-semana4` revisada apunta a `d35079455ad895242aabb5d4530ed8b309215658`. Tiene diferencias en HomePage, entre ellas el aviso de privacidad recuperado en esta propuesta. No es la rama personal confirmada del responsable QA; no se reasigna autoría. El código local no publicado del compañero no puede comprobarse desde GitHub.

El commit de evaluación anunciado `11dd2f8` no se resolvió en la revisión previa; esta revisión de UI no acredita su publicación ni sus métricas. Gitleaks y la revocación histórica se siguen documentando por separado en el cierre QA. No se da por autorizado fusionar ninguna rama ni migrar el hosting.

## Reproducir

Desde la raíz, instalar `backend/requirements.txt` en un entorno Python y ejecutar `npm ci --no-audit --no-fund` dentro de `frontend`. Después:

```text
python scripts/ingest.py
python eval/run_integration.py --static-analysis --output tmp/http-estatico
python eval/run_integration.py --output tmp/http-sin-estatico
```

Usar carpetas de salida nuevas para preservar evidencia. El runner fija explícitamente las banderas estáticas y desactiva límites de tráfico solo dentro de su proceso temporal; no cambia variables del despliegue. En `frontend`: `npm test`, `npm run lint`, `npm run build`, `npm audit`, `npm audit --omit=dev`. El nuevo workflow `integration-tests.yml` reproduce las dos configuraciones HTTP en Linux y publica reportes.

## Evidencias

- `evidencias/semana-4/revision-pr19/`: pruebas originales/corregidas, regresiones, auditorías, capturas y exportación UI.
- `evidencias/semana-4/audit-pr19-original.json`: auditoría original sin modificaciones.
- `evidencias/semana-4/revision-pr19-http-antes/`: 8/9 del contrato anterior con bandera activada.
- `evidencias/semana-4/revision-pr19-http-estatico/`: 15/15 con analizadores reales.
- `evidencias/semana-4/revision-pr19-http-sin-estatico/`: 10 aprobadas y cinco omitidas según configuración.
- `evidencias/semana-4/revision-pr19-http-final-estatico/` y `revision-pr19-http-final-sin-estatico/`: repetición aprobada del ejecutor final, con hashes del runner HTTP, fixture GitHub y tests frontend. Conserva 15/15 y 10/10 aplicables, respectivamente.
- `evidencias/semana-4/revision-pr19-http-original/`: primer intento bloqueado porque la copia aislada no tenía ChromaDB; se resolvió mediante ingesta local antes de medir integración.

La primera ejecución del nuevo workflow detectó una importación incorrecta al añadir hashes de trazabilidad. Se corrigió usando `hashlib.sha256` directamente y se repitieron ambas configuraciones completas; las carpetas `http-final-*` registran esa verificación. Los resultados anteriores se conservan con su alcance original.
