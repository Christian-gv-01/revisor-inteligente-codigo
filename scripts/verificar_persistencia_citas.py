"""Compara las citas RAG antes y después de reiniciar un despliegue.

El reinicio se realiza desde la plataforma o con ``docker compose restart``.
Este script no administra infraestructura ni almacena código o credenciales.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx


CODIGO_PRUEBA = "dato = input()\nresultado = eval(dato)\n"


def comparar(antes: dict, actual: dict) -> dict:
    if antes.get("objetivo") != actual.get("objetivo"):
        raise ValueError("El baseline corresponde a otro objetivo.")
    ids_antes = set(antes.get("fuentes_ids", []))
    ids_despues = set(actual.get("fuentes_ids", []))
    return {
        "citas_coincidentes": sorted(ids_antes & ids_despues),
        "continuidad_citas": bool(ids_antes) and ids_antes == ids_despues,
        "persistencia_volumen_verificada": False,
        "alcance": "Comparación HTTP de citas. Requiere evidencia independiente del reinicio y del volumen sin reingesta.",
    }


def analizar(base_url: str, timeout: float) -> dict:
    with httpx.Client(
        base_url=base_url.rstrip("/"),
        timeout=httpx.Timeout(timeout),
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "CODEGUARD-QA-Persistencia/1.0"},
    ) as cliente:
        respuesta = cliente.post(
            "/api/v1/analizar",
            json={"archivo": "persistencia_eval.py", "codigo": CODIGO_PRUEBA},
        )
    respuesta.raise_for_status()
    datos = respuesta.json()
    fuentes = datos.get("fuentes") or []
    ids = sorted({fuente.get("id") for fuente in fuentes if fuente.get("id")})
    if not ids:
        raise RuntimeError("El análisis no devolvió citas; no puede demostrarse persistencia.")
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "estado": datos.get("estado"),
        "fuentes_ids": ids,
        "total_fuentes": len(ids),
        "total_hallazgos": len(datos.get("hallazgos") or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=("capturar", "verificar"))
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    antes = None
    if args.accion == "verificar":
        if not args.baseline.is_file():
            raise SystemExit("No existe el baseline solicitado.")
        antes = json.loads(args.baseline.read_text(encoding="utf-8"))
        if antes.get("objetivo") != args.base_url.rstrip("/"):
            raise SystemExit("El baseline corresponde a otro objetivo.")
    elif args.baseline.exists():
        raise SystemExit("El baseline ya existe; usa otro nombre para conservar la evidencia.")
    actual = analizar(args.base_url, args.timeout)
    actual["objetivo"] = args.base_url.rstrip("/")

    if args.accion == "capturar":
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Baseline guardado con {actual['total_fuentes']} cita(s): {args.baseline}")
        return 0

    comparacion = comparar(antes, actual)
    resultado = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "objetivo": actual["objetivo"],
        "antes": antes,
        "despues": actual,
        **comparacion,
    }
    salida = args.output or args.baseline.with_name("persistencia-despues.json")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Continuidad de citas: {comparacion['continuidad_citas']}")
    print(f"Evidencia: {salida}")
    return 0 if comparacion["continuidad_citas"] else 1


if __name__ == "__main__":
    sys.exit(main())
