"""Auditoría local y reproducible de secretos, historial y empaquetado Docker."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATRONES = {
    "clave_privada": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "github_token": re.compile(r"gh(?:p|o|u|s|r)_[0-9A-Za-z]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "jwt": re.compile(r"eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,}"),
}


def git(*args: str) -> str:
    proceso = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proceso.stdout


def detectar(texto: str) -> list[str]:
    return [nombre for nombre, patron in PATRONES.items() if patron.search(texto)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rastreados = [
        ruta
        for ruta in git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
        if ruta
    ]
    hallazgos: list[dict] = []
    for ruta_relativa in rastreados:
        ruta = ROOT / ruta_relativa
        if not ruta.is_file() or ruta.stat().st_size > 2_000_000:
            continue
        texto = ruta.read_text(encoding="utf-8", errors="replace")
        for tipo in detectar(texto):
            hallazgos.append({"alcance": "archivo_actual", "tipo": tipo, "ruta": ruta_relativa})

    historial = git("log", "-p", "--all", "--", ".", ":(exclude)*.png", ":(exclude)*.jpg", ":(exclude)*.jpeg")
    for tipo in detectar(historial):
        hallazgos.append({
            "alcance": "historial_git",
            "tipo": tipo,
            "ruta": "valor oculto; revisar historial con herramienta especializada",
        })

    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8", errors="replace")
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8", errors="replace")
    checks = {
        "env_no_rastreado": ".env" not in rastreados,
        "logs_no_rastreados": not any(ruta.endswith(".log") or ruta.startswith("logs/") for ruta in rastreados),
        "docker_excluye_env": ".env" in dockerignore,
        "docker_excluye_git": ".git/" in dockerignore,
        "docker_excluye_logs": "*.log" in dockerignore,
        "dockerfile_no_copia_todo": "COPY . " not in dockerfile and "COPY .\n" not in dockerfile,
        "dockerfile_sin_secretos_build_arg": "ARG GEMINI_API_KEY" not in dockerfile,
    }
    aprobado = all(checks.values()) and not hallazgos
    reporte = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "rama": git("branch", "--show-current").strip(),
        "archivos_rastreados_revisados": len(rastreados),
        "checks": checks,
        "hallazgos": hallazgos,
        "resultado": "aprobado" if aprobado else "requiere_revision",
        "nota": "Los valores potenciales nunca se imprimen en este reporte.",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))
    return 0 if aprobado else 1


if __name__ == "__main__":
    sys.exit(main())
