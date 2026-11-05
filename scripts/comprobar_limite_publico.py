"""Prueba acotada de rechazo HTTP, sin solicitudes válidas a Gemini."""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registros = []
    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=20, trust_env=False, follow_redirects=False) as client:
        for numero in range(1, 12):
            r = client.post("/api/v1/agente/analizar", json={})
            retry = r.headers.get("retry-after", "")
            registros.append({"solicitud": numero, "http": r.status_code,
                "retry_after_segundos": int(retry) if retry.isdigit() else None,
                "no_store": r.headers.get("cache-control") == "no-store"})
            if r.status_code not in (422,):
                break
            time.sleep(1)
    ultimo = registros[-1]
    aprobado = ultimo["http"] == 429 and (ultimo["retry_after_segundos"] or 0) > 0 and ultimo["no_store"]
    reporte = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "objetivo": args.base_url,
        "aprobado": aprobado, "solicitudes": registros,
        "alcance": "Verifica rechazo y encabezados; no determina el umbral exacto ni identidad por IP, porque puede existir tráfico previo."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(reporte, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False))
    return 0 if aprobado else 1


if __name__ == "__main__":
    raise SystemExit(main())
