# Cierre técnico de QA — Entrega 4

> Aporte complementario de QA (PR #26): [verificación pública integrada](15-verificacion-publica-integrada.md), con evidencias propias de `0123445-20Alexis`. Su baseline corresponde a una ejecución anterior al reinicio; la comparación posterior y el log de Christian se documentan en el estado consolidado siguiente. Se conserva la procedencia de cada ejecución.

## Estado consolidado — 5 de noviembre de 2026

Esta actualización recoge las evidencias publicadas por Christian en `main` hasta el commit `219069a`. Las secciones posteriores conservan la revisión histórica y su autoría; sus bloqueos de integración y producción deben leerse con este estado consolidado.

### Integración y pruebas

El [PR #25](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/25) se fusionó a `main` en `d80e75c`. Antes de fusionar, las comprobaciones de la candidata `2dd76ad3490b10524674560b025d4e57c8b66a30` finalizaron en `success`:
- [Backend, controles de Agent Lab y ejecutores QA](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521541).
- [Frontend: lint, build y pruebas](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521518).
- [Integración HTTP con y sin análisis estático](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521602).

Las capturas de ejecución local aportadas por Christian registran 223 pruebas backend aprobadas, 71 frontend aprobadas, lint y build correctos. Las 15 HTTP omitidas en la suite frontend habitual se ejecutaron por separado: 15/15 con estático, 10/10 aplicables sin estático y cinco omisiones intencionales. No atribuir estos conteos locales a los logs de CI sin consultarlos.

La integración HTTP emplea FastAPI y ChromaDB reales y Ruff/Bandit reales cuando están habilitados; Gemini y la API externa GitHub son simulados. No mide la precisión del modelo. Evidencias: [integración con estático](evidencias/semana-4/integracion-final-estatico-20261105-revision2/resultado-integracion.json) e [integración sin estático](evidencias/semana-4/integracion-final-sin-estatico-20261105/resultado-integracion.json).

La interfaz y la exportación JSON separan hallazgos contextuales, citas y reglas estáticas. QA-S10/QA-H01 de la revisión inicial y las correcciones QA19-01 a QA19-04 cuentan con evidencia posterior en [la revisión del PR #19](14-revision-qa-pr19.md), su integración y las pruebas posteriores.

### Gemini real y resultados parciales

[sql-completo.json](evidencias/semana-4/agente-real-20261105/sql-completo.json) documenta una ejecución local del agente en `gemini_real`: tres pasos, dos decisiones ejecutadas, informe `analizado`, hallazgo SQL y referencias presentes en las fuentes recuperadas. [sql-degradado-503.json](evidencias/semana-4/agente-real-20261105/sql-degradado-503.json) registra otra ejecución, con distinto fragmento y nombre, que conservó decisiones y análisis estático al fallar el informe contextual. El log aportado identifica HTTP 503 del proveedor en esa fase.

No son una comparación controlada del mismo código. Demuestran casos concretos de éxito y degradación, no disponibilidad general ni métricas de precisión. Los errores 503 reales siguen siendo una limitación observada.

### Validación pública en Railway

URL: https://revisor-inteligente-codigo-production.up.railway.app

Railway mostró despliegue exitoso asociado a la fusión del PR #25. Las consultas públicas de `/health` y `/openapi.json` respondieron 200, y OpenAPI anunció `/api/v1/estatico/analizar` y `/api/v1/agente/analizar`. El SHA completo de cada despliegue no se publica en `/health`; no confundir un identificador de despliegue Railway con un SHA Git.

La [matriz pública posterior a la fusión](evidencias/semana-4/pruebas-publicas-post-merge-20261105.json) obtuvo **26/26 aprobadas**, cero fallos, con fecha UTC `2026-11-05T21:03:36.273676+00:00`. P05 y P07 ya cumplen la sanitización 422 comprobada por sus aserciones. Los reportes previos de 24/26 se conservan como históricos.

Esta matriz comprueba disponibilidad, entradas, ZIP, validación de URLs GitHub y AST local. No acredita un análisis Gemini real por sí sola; esa evidencia pública está en las capturas de citas siguientes.

### Citas antes y después del reinicio

El primer intento de captura falló tras un 503 del proveedor y no produjo baseline. Después se obtuvo un análisis público `analizado` con un hallazgo y tres fuentes. Se coordinó el reinicio desde Railway y se repitió el análisis:
- [Antes](evidencias/semana-4/persistencia-antes-20261105.json): 16:29:32 del 5 de noviembre, America/Guayaquil.
- [Después y comparación](evidencias/semana-4/persistencia-despues-20261105.json): 16:31:45 del mismo día.
- [Log del reinicio](evidencias/semana-4/reinicio-railway-20261105.png): apagado, montaje del volumen, proceso UID 10001, mensaje de índice documental persistente recuperado y arranque completado.

Ambos análisis devolvieron las fuentes `seguridad_python-001`, `seguridad_python-004` y `seguridad_python-005`, y un hallazgo. **`continuidad_citas: true`**.

El comparador mantiene deliberadamente `persistencia_volumen_verificada: false`: la igualdad de IDs por HTTP no verifica por sí sola el volumen. El log independiente respalda la recuperación operacional del índice en este reinicio; no acredita una auditoría de integridad de todo el volumen, backups ni una prueba con marca única no regenerable. No modificar el JSON para convertir este alcance en una certificación más amplia.

### Pendientes que permanecen abiertos

- **QA-H02:** confirmar de forma trazable el carácter sintético o la revocación de la credencial histórica, sin publicar su valor. La referencia a una revocación comunicada y una exclusión del detector no equivalen a comprobación independiente.
- **QA-H03:** corregido en esta propuesta mediante captura incremental de stdout/stderr con presupuesto combinado de 1.000.000 bytes, terminación al excederlo y timeout. Las pruebas nuevas usan procesos controlados y herramientas reales; la corrección requiere integración y validación del despliegue. No equivale a cuotas de memoria del analizador o del contenedor. La descripción posterior del hallazgo se conserva como histórica.
- Advertencia de tamaño del paquete frontend y errores 503 reales del proveedor.
- Mantener trazabilidad del SHA de despliegue y distinguir recuperación operacional del índice de verificación completa del volumen.

Se cierran los bloqueos observados de sanitización pública P05/P07, publicación del endpoint estático y ausencia de baseline/reinicio. No se declara una aceptación de seguridad sin reservas ni se cierran los hallazgos pendientes por el solo éxito de las pruebas.

## Revisión histórica — se conserva sin cambios

> Actualización posterior: la revisión del PR #19 y las correcciones propuestas en el PR #23 están en [14-revision-qa-pr19.md](14-revision-qa-pr19.md). Los resultados siguientes conservan el estado de la revisión inicial; no sustituyen la evidencia posterior de integración estática.

Fecha de revisión: 4 de noviembre de 2026, America/Bogota.
Responsable del trabajo actual: cuenta confirmada por el usuario `0123445-20Alexis`.

## Base y resultados propios

Se integró `origin/feature/semana4-ruff-bandit` en el commit base `a394d65`, conservando la sanitización 422 de QA y las protecciones HTTP del compañero. Esta integración en la rama QA no fusiona el PR #10 ni despliega Railway.

- Backend integrado: **179 aprobadas**, incluidas pruebas reales Ruff 0.14.1 y Bandit 1.8.6. Evidencia: `evidencias/semana-4/pytest-integrado.xml`.
- Ejecutores QA: **8 aprobadas**. Evidencia: `evidencias/semana-4/pytest-runners.xml`.
- Las 158 pruebas comunicadas por el compañero no se presentan como ejecución propia de GitHub Actions. Los resultados anteriores son locales, Python 3.12.14 en Windows. El workflow del repositorio utiliza Python 3.13/Linux y se habilita también para esta rama.
- Se preservan las evidencias previas de frontend; no acreditan aún la visualización de resultados estáticos.

## Verificación en GitHub Actions y entrega

La rama de entrega es `feature/entrega-4-qa-seguridad-documentacion` y está publicada en el [PR #12, en borrador](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/12), con base en `feature/semana4-ruff-bandit`.

GitHub Actions confirmó **success** para el commit `66d7f4218a72d64392b2b309743a2ad2c9d3dfe6`, tanto en el [evento push](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/41956636926) como en el [evento pull_request](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/41956677118). En Linux con Python 3.13 finalizaron correctamente la validación de sintaxis, las pruebas del backend, las pruebas de los ejecutores QA y la publicación del artefacto `qa-results` con los reportes JUnit. Estos enlaces acreditan esa revisión concreta; los conteos y tiempos locales se conservan por separado.

La entrega QA queda preparada para revisión del equipo. La aprobación de CI no sustituye las comprobaciones de producción pendientes que se detallan a continuación.

## Aceptación del contrato estático

| Caso | Validación | Resultado |
|---|---|---|
| QA-S01 | Endpoint autónomo sin Gemini | Suite integrada aprobada |
| QA-S02 | Código, Python, ZIP, GitHub con análisis estático | Aprobado; GitHub/Gemini simulados en contratos |
| QA-S03 | Las cuatro modalidades con bandera apagada | Aprobado: campo omitido y motor no invocado |
| QA-S04 | `completo`, `parcial`, `no_disponible` conservan abstención RAG | 12 combinaciones aprobadas |
| QA-S05 | Archivo relativo del informe coincide con el contenedor | Aprobado en cuatro modalidades |
| QA-S06 | Ruff/Bandit reales no ejecutan payload que intenta escribir un archivo | Aprobado; no aparece la marca y el temporal se elimina |
| QA-S07 | Subprocesos sin clave de Gemini y stderr privado | Aprobado |
| QA-S08 | Errores, timeout, herramientas ausentes y JSON inválido | Suite heredada aprobada |
| QA-S09 | Alertas estáticas sin `fuentes` ni `referencias` RAG inventadas | Aprobado |
| QA-S10 | Visualización React y exportación JSON | Pendiente de Frontend |

Estados reales del contrato: el informe usa `completo`, `parcial`, `no_disponible`; cada herramienta usa `ok`, `error`, `timeout`, `no_disponible`. No traducir `parcial` o una lista vacía a «código seguro».

## Hallazgos que deben revisar los responsables

### QA-H01 — Frontend todavía descarta el bloque estático

La revisión del adaptador y de `frontend/src/services/report.ts` muestra que el modelo/exportador actual conserva archivos, fuentes y hallazgos RAG, pero no `analisis_estatico`. Debe implementarlo Frontend y después repetirse la aceptación de pantalla y exportación para las cuatro modalidades. Es revisión de código, no una prueba visual ejecutada.

### QA-H02 — Cadena con formato JWT en historial de evaluación

La auditoría actualizada devuelve `requiere_revision`, no cero hallazgos. Localización: commit `288616b3fe1be68a52f1971b8713e87c0a1cba80`, archivo `eval/preguntas_referencia_final.json`, caso P26 («Token de acceso codificado»). El contexto indica un fixture de evaluación. El propietario debe confirmar que es sintético y no utilizable; no se probó el token contra ningún servicio ni se reprodujo su valor en la evidencia. Si fuese real, corresponde revocarlo y coordinar la corrección del historial con el equipo.

### QA-H03 — Límite de salida de subprocess posterior a la captura

`static_analysis._ejecutar` captura stdout/stderr con PIPE y verifica 1 MB después de terminar. El límite rechaza la salida publicada, pero no impone un máximo de memoria durante la captura. Mantener esta limitación explícita y coordinar captura acotada o cuotas de contenedor con Backend. El timeout y el límite de entrada no equivalen a aislamiento de CPU, memoria o red.

## Producción y persistencia

Matriz pública propia ejecutada: **24/26 aprobadas**, evidencia `evidencias/semana-4/pruebas-publicas.json`. P05 falla porque el 422 contiene `input`; P07 falla porque refleja el marcador sintético del código excesivo. La sanitización está implementada en esta rama, pero no aparece aplicada en la respuesta pública. Prioridad: integrar/desplegar la corrección y repetir ambos casos. No se almacenaron cuerpos sensibles en el informe. La ejecución se realizó sobre la aplicación pública disponible, cuyo SHA no se anuncia en `/health`.

La URL obtenida de la evidencia del equipo es https://revisor-inteligente-codigo-production.up.railway.app . Se comprobaron `/health` y `/openapi.json`: el endpoint estático no figura todavía. No atribuir las pruebas locales de Ruff/Bandit a Railway.

Prueba acotada adicional: nueve solicitudes inválidas devolvieron 422 y la décima devolvió **429**, `Retry-After: 25` y `Cache-Control: no-store`. Evidencia: `evidencias/semana-4/limite-publico.json`. Existía tráfico previo; no se infiere de esta secuencia el umbral por visitante ni su identidad detrás del proxy.

El responsable no puede reiniciar el servicio en esta sesión. La persistencia remota queda pendiente de verificación propia. El script de comparación fue corregido para rechazar baselines de otra URL, evitar sobrescribir el baseline y no confundir coincidencia de citas con conservación del volumen.

Se intentó capturar el baseline con un único análisis sintético `eval(input())` en `/api/v1/analizar`. La respuesta fue **HTTP 502**, por lo que no se creó `persistencia-antes.json` ni se obtuvo evidencia de citas. La causa del 502 requiere revisar logs privados de Backend/Railway; no se atribuye automáticamente a Gemini ni al RAG.

Los informes HTTP omiten cuerpos y mensajes de excepción al guardar evidencia para evitar registrar accidentalmente secretos. El ejecutor público respeta 10 unidades ponderadas por ventana de 61 segundos. Su tiempo por escenario puede incluir espera del limitador local y no es una medición de latencia pura de Railway.

## Condición para aceptar la entrega pública

Se requiere integrar los cambios de Frontend, confirmar la revisión desplegada, resolver o aceptar documentadamente los hallazgos, repetir la matriz pública sobre esa revisión y registrar el reinicio coordinado. QA puede entregar ahora el código, pruebas y documentación; no certifica una aceptación de producción completa mientras esos puntos sigan abiertos.

## Revisión de avances del equipo — 5 de noviembre de 2026

Se actualizaron las referencias remotas antes de revisar el informe compartido por Frontend. Revisiones observadas: `origin/main` en `f459ef9`, `origin/feature/frontend-semana4` en `d35079455ad895242aabb5d4530ed8b309215658` y `origin/feature/semana4-ruff-bandit` en `a394d6543b20e77e8abf2e5a1acbe7b78fb58cf2`. La consulta no fusionó estas ramas ni cambió el despliegue.

| Punto comunicado | Comprobación propia | Estado de QA |
|---|---|---|
| Aviso de IA y privacidad | `frontend/src/pages/HomePage.tsx` de la rama de Frontend contiene un aviso visible en modo API: envío de código y contexto a Gemini, análisis sin ejecución y recomendación de no enviar secretos | Implementación comprobada en fuente; falta aceptación visual de la versión integrada/desplegada |
| Gitleaks | Workflow `.github/workflows/secretos.yml` presente y [ejecución 41949973928](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/41949973928) terminada en `success` para `d350794` | Automatización comprobada; el resultado depende de las exclusiones configuradas |
| Credencial histórica | `.gitleaksignore` identifica exactamente el commit y archivo de QA-H02, regla `jwt`, línea 336 | Es el mismo hallazgo. Rotación comunicada por el compañero, no verificada directamente por QA; excluirlo no prueba su revocación |
| Comparación de evaluaciones, commit `11dd2f8` | No disponible tras `git fetch`; la API de commits devolvió HTTP 422 para ese identificador y el documento remoto revisado termina en la sección 9 | Solicitar publicación de ese commit o su SHA completo; no se da por verificada la nueva sección 10 ni sus métricas |
| Ruff/Bandit en Frontend | Sin coincidencias de `analisis_estatico` en `frontend/src` de la rama remota revisada | QA-S10/QA-H01 continúan pendientes |
| Cloud Run | El informe lo menciona como pendiente; la URL comprobada por QA corresponde a Railway | No hay evidencia propia de migración a Cloud Run |

La auditoría QA anterior se conserva sin modificar ni ocultar su hallazgo. No se probó la credencial contra servicios externos y no se solicitó compartir su valor. Para cerrar QA-H02 basta una confirmación trazable del responsable sobre su carácter sintético o su revocación, identificando el hallazgo sin exponer el secreto.

### Repetición pública del 5 de noviembre

Se ejecutó de nuevo `scripts/pruebas_produccion.py` contra la URL de Railway y se guardó el resultado en `evidencias/semana-4/pruebas-publicas-2026-11-05.json`: **24/26 aprobadas**, con los mismos fallos P05 y P07 de sanitización del 422. No hubo mejora verificable en esos dos casos; la corrección de la rama QA sigue pendiente de integración y despliegue.

Después de dejar transcurrir una ventana del limitador, se consultó `/openapi.json` y se repitió una sola llamada a `analizar` del script `verificar_persistencia_citas.py`, con su payload sintético habitual y timeout de 90 segundos. OpenAPI devolvió 200 y continúa sin publicar `/api/v1/estatico/analizar`; el análisis volvió a responder **502**. No se creó baseline de citas. Se guardaron únicamente estados HTTP y booleanos en `evidencias/semana-4/revalidacion-cierre-2026-11-05.json`; no se conservaron cuerpos ni mensajes privados del servidor.

Para continuar, Backend debe integrar/desplegar la sanitización del PR #12 y diagnosticar el 502 con logs privados; Frontend debe publicar la integración estática y la comparación anunciada; el responsable del hosting debe proporcionar acceso operativo o coordinar un reinicio después de obtener citas. QA repetirá las aserciones sobre la revisión integrada. Ninguna evidencia de esta revisión acredita un reinicio, una migración a Cloud Run ni un análisis Gemini exitoso.
