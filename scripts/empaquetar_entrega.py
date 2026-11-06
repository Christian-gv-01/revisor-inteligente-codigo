"""Crea un ZIP candidato únicamente desde objetos Git de una revisión exacta."""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def ruta_permitida(nombre: str) -> bool:
    p = PurePosixPath(nombre)
    if p.is_absolute() or ".." in p.parts or "\\" in nombre:
        return False
    if nombre in {"ENTREGA-manifiesto.json", "ENTREGA-estado.md"}:
        return False
    for parte in p.parts:
        parte = parte.casefold()
        if parte in {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".cache"}:
            return False
        if parte == ".env" or (parte.startswith(".env.") and parte != ".env.example"):
            return False
    return p.suffix.lower() not in {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".pem", ".key", ".zip"}


def empaquetar(repo: Path, salida: Path, ref: str = "HEAD", limite: int = 20_000_000) -> dict:
    revision = git(repo, "rev-parse", "--verify", ref + "^{commit}").decode().strip()
    fecha = datetime.fromtimestamp(int(git(repo, "show", "-s", "--format=%ct", revision)), timezone.utc)
    entradas = git(repo, "ls-tree", "-rz", "--full-tree", revision).split(b"\0")
    archivos = []
    contenido = {}
    for entrada in entradas:
        if not entrada:
            continue
        metadatos, nombre_bytes = entrada.split(b"\t", 1)
        modo, tipo, objeto = metadatos.decode().split()
        nombre = nombre_bytes.decode("utf-8")
        if tipo != "blob" or modo not in {"100644", "100755"}:
            raise ValueError(f"Objeto no regular o submódulo: {nombre}")
        if not ruta_permitida(nombre):
            raise ValueError(f"Archivo versionado no permitido: {nombre}")
        datos = git(repo, "cat-file", "blob", objeto)
        contenido[nombre] = (datos, modo)
        archivos.append({"ruta": nombre, "bytes": len(datos), "git_blob": objeto,
                         "sha256": hashlib.sha256(datos).hexdigest(), "modo": modo})
    pdfs = [x["ruta"] for x in archivos if x["ruta"].startswith("docs/presentacion/") and x["ruta"].lower().endswith(".pdf")]
    manifiesto = {"revision": revision, "fecha_commit_utc": fecha.isoformat(), "estado": "candidato_pendiente_revision",
                  "pdf_presentacion": pdfs, "instalacion_limpia_cronometrada": "requiere evidencia humana independiente",
                  "archivos_git": archivos, "criterio": "bytes de objetos Git; no archivos modificados o no versionados del equipo"}
    contenido["ENTREGA-manifiesto.json"] = (json.dumps(manifiesto, ensure_ascii=False, indent=2).encode() + b"\n", "100644")
    estado = (f"# Paquete candidato de CODEGUARD\n\nRevisión Git: {revision}\n\n"
              f"PDF de presentación: {', '.join(pdfs) if pdfs else 'PENDIENTE'}\n\n"
              "La instalación limpia, la aceptación del equipo y el contenido del PDF necesitan revisión independiente.\n"
              "El paquete no acredita entrega al portal ni aprobación del docente.\n")
    contenido["ENTREGA-estado.md"] = (estado.encode(), "100644")
    if salida.exists():
        raise FileExistsError("La salida existe; usar otra carpeta para conservar evidencias.")
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = salida.with_suffix(".zip.tmp")
    if temporal.exists():
        raise FileExistsError("Hay una construcción previa en la carpeta de salida.")
    try:
        with zipfile.ZipFile(temporal, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for nombre, (datos, modo) in sorted(contenido.items()):
                info = zipfile.ZipInfo(nombre, (max(1980, min(2107, fecha.year)), fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second))
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | int(modo[-3:], 8)) << 16
                z.writestr(info, datos)
        if temporal.stat().st_size > limite:
            raise ValueError("El ZIP supera el máximo de 20 MB; no se publica como paquete válido.")
        with zipfile.ZipFile(temporal) as z:
            if z.testzip() is not None or set(z.namelist()) != set(contenido):
                raise ValueError("Contenido o CRC incompatible con el manifiesto.")
            for nombre, (datos, _) in contenido.items():
                if hashlib.sha256(z.read(nombre)).digest() != hashlib.sha256(datos).digest():
                    raise ValueError("Los bytes del ZIP no corresponden con Git.")
        temporal.rename(salida)
    except BaseException:
        temporal.unlink(missing_ok=True)
        raise
    reporte = {"revision": revision, "estado": manifiesto["estado"], "archivo": salida.name,
               "bytes_zip": salida.stat().st_size, "limite_bytes": limite,
               "sha256_zip": hashlib.sha256(salida.read_bytes()).hexdigest(),
               "archivos_git": len(archivos), "archivos_generados": 2, "pdf_presentacion": pdfs,
               "crc_y_hashes_comprobados": True}
    salida.with_suffix(".verificacion.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return reporte


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--ref", default="HEAD")
    p.add_argument("--output", type=Path, default=Path("dist/entrega/CODEGUARD_Semana4.zip"))
    args = p.parse_args()
    print(json.dumps(empaquetar(args.repo, args.output, args.ref), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
