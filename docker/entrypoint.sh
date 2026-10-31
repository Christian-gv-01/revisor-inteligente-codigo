#!/bin/sh
set -eu

if [ -z "${GEMINI_API_KEY:-}" ]; then
  echo "ERROR: GEMINI_API_KEY no configurada. Define el secreto en la plataforma." >&2
  exit 1
fi

: "${CHROMA_PATH:=/data/chroma}"
export CHROMA_PATH
mkdir -p "$CHROMA_PATH"

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

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
