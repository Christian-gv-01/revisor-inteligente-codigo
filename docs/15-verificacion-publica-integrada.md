# Verificación pública de la entrega integrada

Fecha: 5 de noviembre de 2026, America/Bogota. Responsable QA: `0123445-20Alexis`.

URL del agente compartida por el equipo: https://revisor-inteligente-codigo-production.up.railway.app/agente/demo . Aplicación principal: https://revisor-inteligente-codigo-production.up.railway.app/ . Ambas devolvieron HTTP 200; también `/health` y `/openapi.json`.

## Resultados nuevos

| Comprobación propia | Resultado |
|---|---|
| Matriz pública completa | **26/26 aprobadas**, incluyendo P05/P07 de sanitización 422 que fallaban en ejecuciones anteriores |
| Agente en modo AST local | HTTP 200 y `modo=inspeccion_local` confirmado |
| Publicación estática | OpenAPI incluye `/api/v1/estatico/analizar` |
| Ruff/Bandit autónomos en Railway | HTTP 200, `estado=completo`, ambos motores `ok`, una observación estática |
| Análisis público de código sintético | HTTP 200, `estado=analizado`, un hallazgo, tres fuentes y bloque estático completo |
| Baseline de citas | Guardado con tres IDs de fuentes; todavía sin comparación posterior al reinicio |
| Ejecutores QA | Diez regresiones aprobadas tras actualizar el presupuesto del modo AST |

El análisis que antes devolvía 502 respondió correctamente en esta ejecución. Esto acredita una solicitud exitosa; no demuestra ausencia de errores intermitentes ni calidad general de Gemini. QA no sustituyó respuestas del proveedor ni de Railway por mocks en estas solicitudes públicas. La matriz de 26 casos no requiere Gemini; la captura de citas sí utiliza el endpoint normal de análisis.

Las pruebas de integración locales y CI del PR #23 conservan su alcance simulado para Gemini/GitHub. No se mezclan con los resultados públicos de este documento. El modo real del agente ofrece planificación Gemini + RAG, pero esta revisión de la página solo ejercitó su modo AST local; el análisis con citas se hizo en `/api/v1/analizar`, no en `/api/v1/agente/analizar`.

## Revisión observada y alcance

Al actualizar Git, `integration/semana4-candidata` apuntaba a `2dd76ad3490b10524674560b025d4e57c8b66a30`. `main` contenía el merge del PR #25 en `d80e75cadb1a73a3edb921b9ac07b9d671869ddb`, incorporando la candidata. Estos datos son procedencia Git, no una certificación del SHA ejecutado por Railway: la API pública no anuncia esa revisión.

La matriz empezó con el ejecutor anterior y completó los 26 casos sin respuestas 429. Durante la revisión se adaptó el ejecutor para reservar también una unidad por `/api/v1/agente/previsualizar`, conforme a `ENDPOINT_WEIGHTS` del backend candidato. Se añadió `--casos P05 P07` para repetir casos puntuales conservando sus IDs y resultados independientes. Ambas modificaciones se verificaron con regresiones offline; no se alteraron las aserciones de la matriz que aprobó.

## Evidencias

Carpeta: `evidencias/semana-4/produccion-integrada-20261105/`.

- `disponibilidad-agente.json`: URL compartida, modos publicados, endpoints y comprobación inicial P05/P07.
- `pruebas-publicas.json`: ejecución completa, **26/26**, con fecha UTC y duración por caso.
- `analisis-publico.json`: estados HTTP y conteos del motor estático y del análisis con citas, sin cuerpos completos ni errores privados.
- `persistencia-antes.json`: baseline del payload sintético `dato = input()\nresultado = eval(dato)\n`, usando el mismo nombre `persistencia_eval.py` que el script de verificación.
- `pytest-runners.xml`: diez pruebas offline del ejecutor y manejo de evidencias.

Los tiempos de la matriz pueden incluir espera del limitador local; no deben presentarse como latencia pura del servicio. Las evidencias anteriores se preservan como historial, no se reemplazan por los resultados nuevos.

## Persistencia pendiente

No se reinició el servicio desde esta sesión. Guardar un baseline y observar fuentes disponibles no acredita persistencia del volumen. El responsable del hosting debe registrar el volumen, el reinicio y la recuperación del índice sin reingesta; posteriormente QA ejecutará:

```text
python scripts/verificar_persistencia_citas.py verificar --base-url https://revisor-inteligente-codigo-production.up.railway.app --baseline docs/evidencias/semana-4/produccion-integrada-20261105/persistencia-antes.json --output docs/evidencias/semana-4/produccion-integrada-20261105/persistencia-despues.json
```

El script exige el mismo objetivo e IDs completos, y mantiene `persistencia_volumen_verificada=false` porque la evidencia del reinicio/volumen es independiente. No realizar la comparación antes del reinicio ni sobrescribir el baseline.

La matriz pública, la sanitización, el endpoint estático y una ejecución normal con citas quedan comprobados. El cierre de persistencia y los hallazgos de auditoría que requieran confirmación del propietario siguen sujetos a su evidencia específica.
