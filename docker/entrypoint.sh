#!/bin/sh
set -eu

if [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "ERROR: GEMINI_API_KEY no configurada. Define el secreto en la plataforma." >&2
  exit 1
fi

: "${CHROMA_PATH:=/data/chroma}"
export CHROMA_PATH

# El volumen de Railway se monta como root: preparar permisos una sola vez
# por arranque y después ejecutar todas las tareas Python sin privilegios.
if [ "$(id -u)" -eq 0 ]; then
  mkdir -p "$CHROMA_PATH" /data/.cache
  chown -R codeguard:codeguard /data
  exec gosu codeguard /app/entrypoint.sh "$@"
fi

mkdir -p "$CHROMA_PATH"
echo "CODEGUARD: proceso iniciado sin privilegios (UID $(id -u))."

# Ingesta solamente cuando la colección oficial aún no existe o está vacía.
# En reinicios normales usa los datos persistidos en /data.
python - <<'PY'
import runpy

import chromadb

from app.services.rag import DB_PATH

ready = False
client = chromadb.PersistentClient(path=str(DB_PATH))
try:
    try:
        ready = client.get_collection(name="seguridad_python").count() > 0
    except Exception:
        ready = False
finally:
    client.close()

if ready:
    print("CODEGUARD: índice documental persistente recuperado.", flush=True)
else:
    print("CODEGUARD: inicializando índice documental de seguridad...", flush=True)
    runpy.run_path("/app/scripts/ingest.py", run_name="__main__")
PY

# No aceptar automáticamente X-Forwarded-For de un origen no autenticado.
# El encabezado X-Real-IP solo se usa mediante configuración de confianza explícita.
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --no-proxy-headers
