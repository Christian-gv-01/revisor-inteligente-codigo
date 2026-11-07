> Actualización de producto del 7 de noviembre: Directa es la ruta inicial en API
> para código/.py; Agente se elige explícitamente. ZIP/GitHub siguen directos.
> Decisión y evidencia: [ADR E4-13](docs/09-decisiones.md).

# CODEGUARD · Revisor inteligente de código seguro

CODEGUARD revisa Python como texto, sin importarlo ni ejecutarlo. Integra React,
FastAPI, Gemini, recuperación documental con ChromaDB y herramientas Ruff/Bandit.
Entrega hallazgos con fuentes, ubicación y trazabilidad. Si falta respaldo,
se abstiene; si solo se completa una parte, conserva lo útil y lo comunica.

## Versión y evidencias

La validación pública del 7 de noviembre de 2026 corresponde a `c522c24`
(PR #56). El PR #57 incorporó después la conservación del consumo y de los límites
entre presupuestos anidados, sobre `0a6707b`. Sus evidencias distinguen ambas
revisiones. La ficha docente recibida revisaba `605d142`, del 6 de noviembre.
El [cierre actual](docs/37-cierre-verificado.md) relaciona cada requisito y prueba.
La evaluación generativa y sus límites están en la
[comparación de rutas y semanas](docs/18-comparacion-semanas-3-4.md).

URL pública: https://revisor-inteligente-codigo-production.up.railway.app

Las pruebas de software con Gemini simulado no son medidas de precisión del
proveedor. Los resultados históricos conservan su fecha y revisión en
[docs/evidencias](docs/evidencias/semana-4/README.md).

## Funciones y límites

- Código y `.py`: Directa predeterminada y Agente v2 opcional. Al elegir Agente,
  estático y AST obligatorios; decisiones tipadas de
  ampliar contexto ±6 líneas, buscar referencias por categoría y finalizar.
  Máximo cuatro pasos; el revisor principal solicita tres y el evaluador cuatro.
- ZIP/GitHub: hasta cinco Python y 12.000 caracteres combinados; ZIP hasta 5 MB.
  Se analiza por archivo mediante la ruta directa. No atribuirle planificación
  agéntica. El presupuesto requiere aprobación de una instantánea concreta.
- Correcciones: comparar original y propuesta; aprobar solo descarga una copia.
  Sesiones, hashes, caducidad, idempotencia y conflictos vinculan la decisión.
- Severidad: política YAML, valor original conservado y herencia solo de reglas
  citadas, no ambiguas y en la línea validada. No certifica explotabilidad.
- Informe y JSON: fuentes, trazas, estado parcial y auditoría de severidad.
- Demo: ejemplos locales ilustrativos. Agent Lab: `/agente/demo`.

La explicación principal del agente es [docs/08-agente.md](docs/08-agente.md).
La [arquitectura](docs/03-arquitectura.md), los [requisitos](docs/02-requisitos.md)
y el [inventario de fuentes](docs/04-fuentes.md) describen el producto.

## Instalación local

Requisitos: Python 3.13, Node.js 22 y npm. Una clave Gemini es necesaria únicamente
para análisis generativo real. Nunca colocar claves en `VITE_*` ni en Git.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item .env.example .env
# Completar GEMINI_API_KEY solamente en .env para análisis real.
python scripts\ingest.py
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal, desde la raíz:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1
```

Vite redirige `/api` y `/agente` al backend local. En Linux/macOS usar
`source .venv/bin/activate`, `cp` y separadores `/`. La primera ingesta descarga
MiniLM ONNX si no está en caché. No se incluye una base privada en el repositorio.
Consultar [la instalación comprobada](docs/30-instalacion-checkout-limpio.md):
5 min 45 s con herramientas/cachés existentes, sin Gemini real. No acredita una
instalación independiente por otro integrante.

## Docker y Railway

```sh
docker compose config --quiet
docker compose up --build -d
docker compose logs --tail 80 codeguard
```

Abrir http://127.0.0.1:8080. `docker compose down` conserva el volumen;
`down -v` lo elimina. El modelo ONNX entra durante el build. El arranque prepara
el volumen y pasa a UID 10001 antes de ejecutar Python. `/health` usa `PORT` y no
llama a Gemini. Guía completa: [docs/despliegue.md](docs/despliegue.md).

Docker compila presupuesto y correcciones visibles por defecto, comprobados
en la URL pública sobre c522c24. El presupuesto también se activa en el backend Docker: no es posible
usar las rutas antiguas para saltarse la aprobación. Las banderas `VITE_*`
son públicas y se fijan al construir la imagen, no al arrancarla. La aprobación de proyectos y la descarga de una copia revisada se verificaron
mediante HTTP real; los hashes, conflictos y repetición se conservaron.

| Configuración | Propósito |
|---|---|
| `GEMINI_API_KEY` | Secreto solo en backend/plataforma |
| `GEMINI_MODEL` | Modelo disponible en la cuenta |
| `LLM_TIMEOUT_SECONDS`, `LLM_MAX_OUTPUT_TOKENS` | Timeout por llamada y máximo de salida |
| `LLM_RETRY_ATTEMPTS` | Total de intentos por llamada lógica, entre 1 y 3 |
| `ANALYSIS_TOTAL_SECONDS`, `AGENT_TOTAL_SECONDS`, `PROJECT_TOTAL_SECONDS` | Plazos compartidos acotados a 45/150/150 s |
| `CHROMA_PATH` | Volumen persistente; `/data/chroma` en Docker |
| `RAG_MAX_DISTANCE` | Distancia máxima; no es confianza |
| `PROJECT_BUDGET_ENABLED` | Exigir aprobación de ZIP/GitHub en backend |
| `VITE_PROJECT_BUDGET_ENABLED` | Build de interfaz del presupuesto; debe coincidir con backend |
| `VITE_CORRECTIONS_API_ENABLED` | Build de previsualización y descarga aprobada |
| `RATE_LIMIT_ENABLED`, `CONCURRENCY_LIMIT_ENABLED` | Protección por proceso; Docker las activa |
| `STATIC_ANALYSIS_ENABLED` | Estático en rutas directas; agente lo ejecuta siempre |
| `TRUST_RAILWAY_REAL_IP` | Solo con ingreso exclusivo por proxy confiable |

`backend/app/config/settings.py` concentra parámetros. Síntesis: temperatura
0,2; planificador: 0. Los valores efectivos de Railway se registran por corrida.
No existe fallback Groq funcional. Las variables heredadas `LLM_PROVIDER`,
`LLM_FALLBACK_PROVIDER`, `LLM_TEMPERATURE` y `LLM_MAX_RETRIES` no cambian esa lógica.
La [política de severidad](docs/35-severidad-derivada-herencia.md) distingue
prioridad, confianza de Bandit y severidad resultante.

## Verificación

```sh
cd backend
python -m pytest tests ../qa ../eval -q
cd ../frontend
npm test
npm run lint
npm run build
```

La suite unitaria omite HTTP cuando no se configura servidor; omisión no es
aprobación. Integración con proveedores simulados:

```sh
python eval/run_integration.py --static-analysis --output tmp/http-estatico-nuevo
python eval/run_integration.py --output tmp/http-sin-estatico-nuevo
python qa/run_agent_v2_browser.py --output tmp/agente-browser-nuevo
python qa/run_project_budget_browser.py --output tmp/presupuesto-browser-nuevo
```

Pruebas públicas sin llamadas generativas y comparación real separada:

```sh
python scripts/pruebas_produccion.py --base-url https://URL --output tmp/publicas-nuevas.json
python eval/comparar_rutas.py --validar
```

El [protocolo](docs/27-protocolo-comparacion-rutas.md) explica cómo autorizar la
corrida real de cuarenta solicitudes, conservar fallos y reportar consumo.
No repetir para elegir solo resultados favorables.

## Entrega y limitaciones

[Índice documental](docs/README.md), [presentación](docs/presentacion/README.md),
[datos y privacidad](docs/tratamiento-datos.md), [decisiones](docs/09-decisiones.md),
[aportes](docs/11-aportes-ia.md) y [cierre verificable](docs/37-cierre-verificado.md).

Puede haber falsos positivos/negativos. Citas resolubles no garantizan pertinencia
semántica. El corpus curado es pequeño. El proveedor puede fallar o limitar cuota.
Los plazos son cooperativos y dejar de esperar en el navegador no cancela una
operación ya aprobada. No hay autenticación ni cuotas por persona; los límites
por proceso requieren coordinación para varias réplicas. Revisar el resultado
antes de cambiar software. El ensayo oral, las aceptaciones y los originales
académicos faltantes deben aportarlos personas; no se fabrican como evidencia.

El paquete se genera desde una revisión Git exacta con
`scripts/empaquetar_entrega.py`, máximo 20 MB, sin `.env`, cachés ni dependencias.
La generación del paquete no acredita envío al docente.
