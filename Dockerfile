# CODEGUARD: frontend compilado + FastAPI en un único servicio.
FROM node:22-bookworm-slim AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
ARG VITE_PROJECT_BUDGET_ENABLED=1
ARG VITE_CORRECTIONS_API_ENABLED=1
ENV VITE_PROJECT_BUDGET_ENABLED=${VITE_PROJECT_BUDGET_ENABLED} \
    VITE_CORRECTIONS_API_ENABLED=${VITE_CORRECTIONS_API_ENABLED}
RUN npm run build

FROM python:3.13-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    SERVE_FRONTEND=1 \
    RATE_LIMIT_ENABLED=1 \
    CONCURRENCY_LIMIT_ENABLED=1 \
    STATIC_ANALYSIS_ENABLED=1 \
    PROJECT_BUDGET_ENABLED=1 \
    ANONYMIZED_TELEMETRY=False \
    OTEL_SDK_DISABLED=true \
    TRUST_RAILWAY_REAL_IP=0 \
    CHROMA_PATH=/data/chroma \
    HOME=/opt/codeguard \
    XDG_CACHE_HOME=/data/.cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 codeguard \
    && useradd --system --uid 10001 --gid codeguard --home-dir /opt/codeguard codeguard

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/backend/requirements.txt

# ChromaDB 1.5.9 guarda MiniLM ONNX bajo Path.home()/.cache/chroma.
# El HOME del usuario coincide con esta ruta, también después de gosu.
# Descargar y verificar una inferencia durante el build, fuera del volumen /data.
RUN mkdir -p /opt/codeguard \
    && python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; vectors = ONNXMiniLM_L6_V2()(['seguridad Python']); assert len(vectors[0]) == 384" \
    && chmod -R a+rX /opt/codeguard

COPY backend/app /app/backend/app
COPY knowledge /app/knowledge
COPY scripts /app/scripts
COPY --from=frontend-builder /build/frontend/dist /app/frontend/dist
COPY docker/entrypoint.sh /app/entrypoint.sh

RUN mkdir -p /data/chroma /data/.cache \
    && chown -R codeguard:codeguard /data \
    && chmod 755 /app/entrypoint.sh

USER root
WORKDIR /app/backend
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=8s --start-period=180s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health',timeout=5).read()" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

