# Evidencias verificables — Semana 4

## Reglas

- Cada resultado debe provenir de un comando ejecutado.
- No guardar `.env`, claves, tokens, código privado ni valores del panel.
- Distinguir `local` de `público` en nombres y contenido.
- Las capturas deben mostrar URL, fecha o contexto suficiente para reproducirlas.
- Un archivo pendiente no se reemplaza por una afirmación sin evidencia.

## Inventario

| Evidencia | Estado inicial | Cómo se genera |
|---|---|---|
| `pruebas-locales.json` | 26/26 aprobados | `scripts/pruebas_produccion.py` contra localhost |
| `integracion-http/resultado-integracion.json` | 9/9 aprobadas | FastAPI y ChromaDB reales; proveedor controlado |
| `pruebas-publicas.json` | Bloqueada hasta disponer de URL | Mismo script contra HTTPS público |
| `auditoria-secretos.json` | Aprobada, 0 hallazgos | `scripts/auditar_secretos.py` |
| `pruebas-automatizadas.md` | Backend, frontend y Docker documentados | pytest, Vitest, ESLint, build y Compose |
| `persistencia-antes.json` | Bloqueada hasta análisis real | Captura de citas antes del reinicio |
| `persistencia-despues.json` | Bloqueada hasta reinicio | Comparación posterior |
| Capturas de hosting | Bloqueadas hasta despliegue | URL HTTPS, volumen, variables ocultas y logs |

## Evidencia pública mínima

1. Interfaz en el dominio HTTPS.
2. `/health` en el mismo dominio.
3. Resultado de un análisis real con citas.
4. 26 escenarios del runner aprobados.
5. Volumen montado en `/data`.
6. Mismas citas después de reiniciar o volver a desplegar.
7. Variables visibles solo por nombre, con valores ocultos.

El estado final y las limitaciones se actualizarán después de cada ejecución.
