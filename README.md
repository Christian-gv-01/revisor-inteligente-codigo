# CODEGUARD — Revisor Inteligente de Código Seguro

CODEGUARD analiza código Python como texto para identificar riesgos de seguridad sin ejecutarlo. Combina una API FastAPI, una interfaz React, Gemini y recuperación documental con ChromaDB. Los hallazgos deben incluir citas recuperadas; si no existe evidencia suficiente, el sistema se abstiene.

## Estado de la Entrega 4

- Rama QA: `feature/entrega-4-qa-seguridad-documentacion`.
- URL pública HTTPS: **pendiente de publicación por el responsable del despliegue**. No se declara una URL local como evidencia pública.
- Contenedor: preparado para servir frontend y API desde un mismo origen.
- Persistencia: ChromaDB utiliza un volumen externo configurable.
- Pruebas públicas: `scripts/pruebas_produccion.py` incluye 26 escenarios seguros.

## Funcionalidades

- Análisis de código pegado y archivos `.py`.
- Análisis de hasta cinco archivos Python dentro de un ZIP validado.
- Descarga limitada de repositorios públicos de GitHub.
- RAG con fuentes, citas y abstención verificable.
- Agent Lab con herramientas AST de solo lectura.
- Interfaz React con hallazgos, trazabilidad documental y exportación.

## Arquitectura

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

## Controles de seguridad

- Límites de tamaño y cantidad para código, `.py`, ZIP y GitHub.
- Rechazo de traversal, enlaces especiales, ZIP cifrados, bytes nulos y texto no UTF-8.
- Dominio fijo `github.com` y llamadas solamente a `api.github.com`, sin redirecciones.
- Separación explícita entre instrucciones confiables y código/documentos no confiables.
- Citas RAG verificadas; referencias inventadas producen abstención.
- Errores controlados para 429, 503, timeouts y respuestas inválidas.
- Errores 422 sanitizados para no reflejar código o posibles secretos.

## Limitaciones

- No hay autenticación, rate limiting global ni cuotas por usuario. No se recomienda mantener una demo pública con una clave de pago sin control de acceso.
- `/health` no demuestra por sí solo que Gemini y RAG funcionen.
- Las herramientas AST son heurísticas y pueden producir falsos positivos o negativos.
- Las pruebas con mocks validan contratos, no la calidad real de Gemini.
- La URL, el reinicio en la plataforma y las capturas públicas deben obtenerse después del despliegue real.

## Documentación

- [Propuesta](docs/01-propuesta.md)
- [Requisitos y trazabilidad](docs/02-requisitos.md)
- [Arquitectura](docs/03-arquitectura.md)
- [RAG](docs/06-rag.md)
- [Evaluación](docs/07-evaluacion.md)
- [Pruebas de Entrega 4](docs/08-pruebas.md)
- [Decisiones](docs/09-decisiones.md)
- [Aportes y uso de IA](docs/11-aportes-ia.md)
- [Evidencias de semana 4](docs/evidencias/semana-4/README.md)
