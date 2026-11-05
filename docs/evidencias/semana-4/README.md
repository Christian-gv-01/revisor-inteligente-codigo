# Evidencias verificables — Semana 4

> Estado actualizado al 5 de noviembre de 2026: matriz pública 26/26 y continuidad de tres citas tras reinicio, con log independiente de recuperación del índice. CI de backend, frontend y HTTP aprobado para la candidata. QA-H02 y QA-H03 siguen abiertos. Ver [cierre consolidado](../../12-cierre-qa-entrega4.md). Los reportes previos se conservan como históricos.

## Reglas

- Cada resultado debe provenir de un comando ejecutado.
- No guardar `.env`, claves, tokens, código privado ni valores del panel.
- Distinguir `local` de `público` en nombres y contenido.
- Las capturas deben mostrar URL, fecha o contexto suficiente para reproducirlas.
- Un archivo pendiente no se reemplaza por una afirmación sin evidencia.

## Evidencias posteriores a la integración

| Evidencia | Resultado y alcance |
|---|---|
| [pruebas-publicas-post-merge-20261105.json](pruebas-publicas-post-merge-20261105.json) | 26/26 en Railway; P05 y P07 aprobados |
| [integracion-final-estatico-20261105-revision2/resultado-integracion.json](integracion-final-estatico-20261105-revision2/resultado-integracion.json) | 15/15 HTTP; ChromaDB y Ruff/Bandit reales, Gemini/GitHub externo simulados |
| [integracion-final-sin-estatico-20261105/resultado-integracion.json](integracion-final-sin-estatico-20261105/resultado-integracion.json) | 10/10 aplicables y cinco omisiones intencionales |
| [agente-real-20261105/sql-completo.json](agente-real-20261105/sql-completo.json) | Agente local Gemini real, informe analizado, dos decisiones, tres pasos |
| [agente-real-20261105/sql-degradado-503.json](agente-real-20261105/sql-degradado-503.json) | Otro fragmento, informe parcial, decisiones y estático conservados; 503 identificado en el log aportado |
| [persistencia-antes-20261105.json](persistencia-antes-20261105.json) | Análisis público con un hallazgo y tres fuentes, antes del reinicio |
| [persistencia-despues-20261105.json](persistencia-despues-20261105.json) | Mismas tres fuentes y un hallazgo; continuidad true; volumen no verificado por el comparador HTTP |
| [reinicio-railway-20261105.png](reinicio-railway-20261105.png) | Log independiente de apagado, volumen, recuperación del índice y arranque |
| [CI backend](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521541), [frontend](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521518), [HTTP](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/42106521602) | Success para candidata 2dd76ad, antes de fusionar PR #25 |

Los nombres históricos `persistencia-antes.json` y `persistencia-despues.json` de la tabla siguiente no son los archivos generados en la verificación final: las evidencias efectivas incluyen el sufijo `-20261105`. La continuidad HTTP y el log respaldan recuperación operacional en el reinicio documentado; no constituyen auditoría completa del volumen.

## Inventario histórico

| Evidencia | Estado inicial | Cómo se genera |
|---|---|---|
| `pruebas-locales.json` | 26/26 aprobados | `scripts/pruebas_produccion.py` contra localhost |
| `integracion-http/resultado-integracion.json` | 9/9 aprobadas | FastAPI y ChromaDB reales; proveedor controlado |
| `pruebas-publicas.json` | 24/26; dos fallos de sanitización 422 | Mismo script contra HTTPS público |
| `pruebas-publicas-2026-11-05.json` | Repetición: 24/26; persisten P05/P07 | Mismo script contra Railway el 5 de noviembre |
| `revalidacion-cierre-2026-11-05.json` | Endpoint estático ausente; análisis 502; sin baseline | Consulta OpenAPI y un análisis sintético con el helper de persistencia |
| `auditoria-secretos.json` | Histórico previo a actualizar ramas | `scripts/auditar_secretos.py` |
| `auditoria-secretos-integrado.json` | Requiere revisar JWT de fixture | Historial ampliado tras fetch |
| `pytest-integrado.xml` | 179 aprobadas | Suite integrada con Ruff/Bandit reales |
| `pytest-runners.xml` | 8 aprobadas | Protección de evidencias y comparación de citas |
| [GitHub Actions](https://github.com/Christian-gv-01/revisor-inteligente-codigo/actions/runs/41956677118) | Aprobado para `66d7f42` en Linux/Python 3.13 | Backend, ejecutores QA y artefacto `qa-results` |
| `pruebas-automatizadas.md` | Backend, frontend y Docker documentados | pytest, Vitest, ESLint, build y Compose |
| `persistencia-antes.json` | Bloqueada hasta análisis real | Captura de citas antes del reinicio |
| `persistencia-despues.json` | Bloqueada hasta reinicio | Comparación posterior |
| Capturas de hosting | Pendientes de acceso del responsable; HTTPS ya comprobado por HTTP | Volumen, variables ocultas y logs de reinicio |

## Evidencia pública mínima

1. Interfaz en el dominio HTTPS.
2. `/health` en el mismo dominio.
3. Resultado de un análisis real con citas.
4. 26 escenarios del runner aprobados.
5. Volumen montado en `/data`.
6. Mismas citas después de reiniciar o volver a desplegar.
7. Variables visibles solo por nombre, con valores ocultos.

El estado final y las limitaciones se actualizarán después de cada ejecución.
