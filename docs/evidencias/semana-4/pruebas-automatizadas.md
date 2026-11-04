# Ejecución automatizada — Entrega 4

Fecha de ejecución: 4 de noviembre de 2026. Zona horaria: America/Bogota.

## Backend

Comando ejecutado desde `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pytest tests -q
```

Resultado observado:

```text
........................................................................ [ 62%]
...........................................                              [100%]
115 passed in 2.90s
```

La ejecución incluye las regresiones de Agent Lab, análisis, ChromaDB, prompt injection, GitHub, errores del LLM, RAG, archivos y ZIP.

## Frontend

Comandos ejecutados desde `frontend/`:

```powershell
npm test
npm run lint
npm run build
```

Resultados observados:

- 58 pruebas aprobadas.
- 9 pruebas HTTP omitidas porque requieren el ejecutor de integración temporal específico.
- 0 pruebas fallidas.
- ESLint finalizó sin errores.
- TypeScript y Vite compilaron 749 módulos correctamente.
- Vite informó una advertencia no bloqueante por un chunk principal superior a 500 kB.

Las nueve pruebas HTTP omitidas en la suite habitual se ejecutaron después con
`eval/run_integration.py`: **9/9 aprobadas**. La prueba utilizó FastAPI y ChromaDB
local reales, con el proveedor de IA simulado y cero llamadas externas. El reporte
estructurado está en `integracion-http/resultado-integracion.json`.

## Escenarios HTTP locales

`scripts/pruebas_produccion.py` se ejecutó contra `http://127.0.0.1:8765` usando un servidor Uvicorn temporal y aislado de servicios externos.

Resultado: **26/26 aprobados**. El detalle estructurado está en `pruebas-locales.json`.

## Docker

- `docker compose config --quiet`: código de salida 0.
- Docker CLI: 29.5.2.
- Docker Compose: v5.1.4.
- Docker Desktop Engine: no estaba iniciado; no se construyó el contenedor ni se ejecutó todavía la prueba local de reinicio.

## Alcance

Estos resultados acreditan el código y la instancia local. No acreditan todavía la URL pública, HTTPS administrado por la plataforma ni la persistencia del volumen remoto.
