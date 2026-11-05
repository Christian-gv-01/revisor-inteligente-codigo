# Cierre técnico de QA — Entrega 4

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
