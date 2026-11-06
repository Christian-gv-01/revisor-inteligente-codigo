# CODEGUARD — Revisor Inteligente de Código Seguro

> Actualización del 6 de noviembre: frontend y backend de confirmación integrados
> mediante PR #36, commit `caecd71`, con CI en main y despliegue verificados.
> La evaluación real y sus límites se registran en
> [validación posterior a la integración](docs/24-validacion-real-postmerge.md).
> La previsualización real sigue deshabilitada por defecto en el frontend público;
> habilitarla requiere la decisión del equipo y un nuevo build.

CODEGUARD analiza código Python como texto para identificar riesgos de seguridad sin ejecutarlo. Combina una API FastAPI, una interfaz React, Gemini y recuperación documental con ChromaDB. Los hallazgos deben incluir citas recuperadas; si no existe evidencia suficiente, el sistema se abstiene.

## Estado de la Entrega 4

Actualización del 5 de noviembre de 2026:

La revisión documental actual toma como base `65675e2`, que integra el agente en
React mediante PR #31. Su [validación local](docs/17-agente-integrado.md) registra
250 pruebas backend/QA, 76 frontend y 17/17 HTTP con estático; la configuración
alternativa registra 12/12 aplicables y cinco omisiones. Gemini y GitHub externo
son simulados en esas pruebas. El agente ejecuta Ruff/Bandit en ambas configuraciones.
La evidencia pública siguiente pertenece a corridas anteriores identificadas;
no certifica automáticamente el despliegue de PR #31.

Documentación y responsabilidades: [índice](docs/README.md),
[estado de cierre](docs/19-cierre-documental.md) y [aportes](docs/11-aportes-ia.md).

Evidencia previa conservada:
- Integración fusionada a `main` mediante [PR #25](https://github.com/Christian-gv-01/revisor-inteligente-codigo/pull/25), commit `d80e75c`; evidencias posteriores publicadas hasta `219069a`.
- Backend, frontend e integración HTTP de la candidata aprobados en GitHub Actions. En Windows se registraron 223 pruebas backend y 71 frontend aprobadas, más 15/15 HTTP con Ruff/Bandit y 10/10 aplicables sin estático.
- URL pública: https://revisor-inteligente-codigo-production.up.railway.app . Salud y OpenAPI responden; el endpoint estático ya figura en el esquema público.
- [Matriz pública posterior a la fusión](docs/evidencias/semana-4/pruebas-publicas-post-merge-20261105.json): **26/26 aprobadas**, incluidos P05/P07 de sanitización 422.
- Agente Gemini real: evidencia local de una ejecución completa y otra degradada por 503, con traza conservada. Son casos distintos y no demuestran disponibilidad general.
- Dos análisis públicos conservaron un hallazgo y las mismas tres fuentes, con `continuidad_citas: true`. El equipo los presentó como antes/después de un reinicio, pero la imagen versionada muestra el comparador, no los logs de Railway. Falta el respaldo independiente del reinicio/volumen; la comparación HTTP no verifica por sí sola persistencia física.
- Seguridad: QA-H03 incorpora captura acotada durante la lectura de stdout/stderr (ver [contrato estático](docs/10-analisis-estatico.md)); requiere validación de la revisión desplegada. El cierre documental de QA-H02 sigue pendiente. Persisten los 503 observados y la advertencia de tamaño del paquete frontend.
- Estado, enlaces de CI, evidencias y límites en [Cierre técnico de QA](docs/12-cierre-qa-entrega4.md).

## Funcionalidades

- Análisis de código pegado y archivos `.py`.
- Análisis de hasta cinco archivos Python dentro de un ZIP validado.
- Descarga limitada de repositorios públicos de GitHub.
- RAG con fuentes, citas y abstención verificable.
- Agente integrado en la revisión principal de código pegado y archivos `.py`: evidencia Ruff/Bandit y AST para la síntesis RAG, pasos visibles y exportación de la traza. ZIP/GitHub conservan la revisión directa.
- Agent Lab con herramientas AST de solo lectura para inspección técnica.
- Interfaz React con hallazgos, trazabilidad documental y exportación.

## Arquitectura

Contrato, límites y pruebas de la integración: [Agente en la revisión principal](docs/17-agente-integrado.md).

```text
Navegador ──HTTPS──> FastAPI
                      ├── React compilado (/)
                      ├── API (/api/v1/*)
                      ├── Agent Lab (/agente/demo)
                      ├── Gemini
                      └── ChromaDB (/data/chroma en producción)
```

El backend nunca importa ni ejecuta el código recibido. Las claves permanecen en el servidor y no deben utilizar variables `VITE_*`.

## Requisitos

- Python 3.13 para reproducir la imagen de producción.
- Node.js 22 para compilar el frontend.
- Docker Desktop para la ejecución integrada.
- Una clave válida de Gemini solamente para análisis reales.

## Configuración

Copiar `.env.example` como `.env` y completar únicamente los valores locales. `.env` está ignorado por Git y por Docker.

| Variable | Obligatoria | Uso |
|---|---:|---|
| `GEMINI_API_KEY` | Sí, para análisis real | Secreto del proveedor; nunca se publica. |
| `GEMINI_MODEL` | Recomendada | Modelo disponible en la cuenta. |
| `LLM_TIMEOUT_SECONDS` | No | Tiempo máximo de Gemini. |
| `LLM_MAX_OUTPUT_TOKENS` | No | Límite de respuesta. |
| `CHROMA_PATH` | Producción | Ruta del índice persistente; `/data/chroma` en Docker. |
| `RAG_MAX_DISTANCE` | No | Umbral de recuperación documental. |
| `PORT` | Plataforma | Puerto asignado al contenedor. |
| `SERVE_FRONTEND` | Docker | Sirve `frontend/dist` desde FastAPI. |
| `STATIC_ANALYSIS_ENABLED` | No | Activa Ruff/Bandit en rutas directas. El agente y endpoint estático los ejecutan independientemente de esta bandera. |
| `RATE_LIMIT_ENABLED` | Producción | Presupuesto de peticiones por proceso. |
| `CONCURRENCY_LIMIT_ENABLED` | Producción | Máximo de dos solicitudes costosas activas. |
| `TRUST_RAILWAY_REAL_IP` | No | Activar solo con ingreso exclusivo por proxy confiable. |

La síntesis lee `GEMINI_MODEL` (valor predeterminado en código:
`gemini-3.5-flash-lite`), timeout 60 s y máximo de salida 2048 si no se configuran.
El ejemplo `.env` propone timeout 20 s; los valores efectivos deben registrarse
en cada evaluación. La temperatura de síntesis está fijada en código a 0,2 y la
del planificador a 0. Las variables heredadas `LLM_PROVIDER`,
`LLM_FALLBACK_PROVIDER`, `GROQ_MODEL`, `GROQ_API_KEY`, `LLM_TEMPERATURE` y
`LLM_MAX_RETRIES` del ejemplo no seleccionan un proveedor alternativo ni cambian
esos parámetros en la implementación actual. No existe fallback Groq funcional.

`VITE_API_BASE_URL` se configura al compilar el frontend: vacío para el despliegue
del mismo origen; en desarrollo, Vite redirige `/api` al backend local. Nunca
guardar una clave de Gemini en una variable `VITE_*`.

## Ejecución local sin Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd frontend
npm ci
npm run build
cd ..
python scripts\ingest.py
cd backend
python -m uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`; en desarrollo, el frontend también puede iniciarse con `npm run dev`.

Para ese servidor de desarrollo, abrir otra terminal en `frontend/` y ejecutar
`npm run dev`. Compilar React no activa automáticamente su servicio desde FastAPI;
para servir el build sin Vite configurar `SERVE_FRONTEND=1` antes de iniciar el
backend. Docker ya incluye esta configuración.

## Ejecución integrada con Docker

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
docker compose logs --tail 80 codeguard
```

Abrir `http://127.0.0.1:8080`. El volumen `codeguard-data` conserva ChromaDB. Para detener sin borrar datos: `docker compose down`. No utilizar `docker compose down -v` durante la prueba de persistencia.

La guía de hosting y volumen está en [docs/despliegue.md](docs/despliegue.md).

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/health` | Disponibilidad básica. |
| `POST` | `/api/v1/analizar` | Código JSON. |
| `POST` | `/api/v1/archivos` | Archivo `.py`. |
| `POST` | `/api/v1/archivos/zip` | Proyecto ZIP. |
| `POST` | `/api/v1/repositorios/github` | Repositorio público. |
| `POST` | `/api/v1/agente/previsualizar` | Herramientas AST sin IA. |
| `POST` | `/api/v1/agente/analizar` | Agente supervisado y análisis RAG. |
| `POST` | `/api/v1/estatico/analizar` | Ruff/Bandit autónomos, sin Gemini; publicado en OpenAPI. |

## Pruebas

Backend, desde `backend/`:

```powershell
python -m pytest tests -q
```

Frontend:

```powershell
cd frontend
npm test
npm run lint
npm run build
```

Escenarios contra una instancia desplegada:

```powershell
python scripts\pruebas_produccion.py `
  --base-url https://URL-PUBLICA `
  --output docs\evidencias\semana-4\pruebas-publicas.json
```

Persistencia de citas:

```powershell
python scripts\verificar_persistencia_citas.py capturar --base-url https://URL-PUBLICA --baseline docs\evidencias\semana-4\persistencia-antes.json
# Reiniciar o volver a desplegar conservando el volumen.
python scripts\verificar_persistencia_citas.py verificar --base-url https://URL-PUBLICA --baseline docs\evidencias\semana-4\persistencia-antes.json --output docs\evidencias\semana-4\persistencia-despues.json
```

Auditoría de secretos:

```powershell
python scripts\auditar_secretos.py --output docs\evidencias\semana-4\auditoria-secretos.json
```

La matriz completa está en [docs/08-pruebas.md](docs/08-pruebas.md).

Integración HTTP local, desde la raíz con dependencias e índice preparados:

```powershell
python eval/run_integration.py --static-analysis --output tmp/http-estatico
python eval/run_integration.py --output tmp/http-sin-estatico
```

El ejecutor utiliza servicios locales y proveedor simulado; no equivale a la
evaluación de Gemini. Para comprobar también los ejecutores QA desde `backend/`:
`python -m pytest tests ../qa -q`.

La instalación en diez minutos es un criterio de la rúbrica aún pendiente de
medición con un integrante nuevo. Registrar equipo, cachés y tiempo real; no
inferirlo de que los comandos estén documentados.

## Controles de seguridad

- Límites de tamaño y cantidad para código, `.py`, ZIP y GitHub.
- Rechazo de traversal, enlaces especiales, ZIP cifrados, bytes nulos y texto no UTF-8.
- Dominio fijo `github.com` y llamadas solamente a `api.github.com`, sin redirecciones.
- Separación explícita entre instrucciones confiables y código/documentos no confiables.
- Citas RAG verificadas; referencias inventadas producen abstención.
- Errores controlados para 429, 503, timeouts y respuestas inválidas.
- Errores 422 sanitizados para no reflejar código o posibles secretos.

## Limitaciones

- No hay autenticación ni cuotas de tokens por usuario. Existen límites de peticiones y concurrencia por proceso; varias réplicas requieren coordinación compartida.
- `/health` no demuestra por sí solo que Gemini y RAG funcionen.
- Las herramientas AST son heurísticas y pueden producir falsos positivos o negativos.
- Las pruebas con mocks validan contratos, no la calidad real de Gemini.
- Las evidencias públicas y de comparación de citas están versionadas; falta el log independiente del reinicio. No certifican disponibilidad futura ni la integridad completa del volumen.

## Documentación

- [Índice y orden de lectura](docs/README.md)
- [Matriz de cierre documental y pendientes](docs/19-cierre-documental.md)

- [Propuesta](docs/01-propuesta.md)
- [Requisitos y trazabilidad](docs/02-requisitos.md)
- [Arquitectura](docs/03-arquitectura.md)
- [Fuentes y materia prima](docs/04-fuentes.md)
- [Levantamiento: instrumento y estado real](docs/levantamiento.md)
- [RAG](docs/06-rag.md)
- [Evaluación](docs/07-evaluacion.md)
- [Comparación Semanas 3 y 4](docs/18-comparacion-semanas-3-4.md)
- [Aviso de IA y tratamiento de datos](docs/tratamiento-datos.md)
- [Pruebas de Entrega 4](docs/08-pruebas.md)
- [Cierre QA e integración estática](docs/12-cierre-qa-entrega4.md)
- [Decisiones](docs/09-decisiones.md)
- [Aportes y uso de IA](docs/11-aportes-ia.md)
- [Evidencias de semana 4](docs/evidencias/semana-4/README.md)


