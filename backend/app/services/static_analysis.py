"""Análisis estático seguro mediante Ruff (calidad) y Bandit (seguridad).

El código recibido es solamente dato; jamás se importa, ejecuta o entrega a un
intérprete Python. Ruff usa stdin y Bandit analiza un archivo temporal aislado.
Ambas herramientas se lanzan sin shell, con límites de tiempo y tamaño.
"""
from __future__ import annotations

import json
import os
import re
import subprocess  # nosec B404 - solo ejecuta herramientas internas.
import sys
import tempfile
import threading
import time
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, Field

MAX_CHARS = 12_000
MAX_STDOUT = 1_000_000
_READ_CHUNK = 64 * 1024
TOOL_TIMEOUT = 12
_SAFE_PART = re.compile(r"^[A-Za-z0-9_.-]{1,120}$", re.ASCII)
_SEVERIDADES = {"HIGH": "alta", "MEDIUM": "media", "LOW": "baja"}


class HallazgoEstatico(BaseModel):
    herramienta: Literal["ruff", "bandit"]
    regla: str = Field(min_length=1, max_length=40)
    tipo: Literal["seguridad", "calidad"]
    linea: int = Field(ge=1)
    columna: int | None = Field(default=None, ge=1)
    severidad: Literal["critica", "alta", "media", "baja"]
    titulo: str
    descripcion: str
    confianza: Literal["alta", "media", "baja"] | None = None
    referencia: str | None = None


class EstadoHerramienta(BaseModel):
    herramienta: Literal["ruff", "bandit"]
    estado: Literal["ok", "no_disponible", "timeout", "error"]
    hallazgos: int = 0


class ResultadoEstatico(BaseModel):
    archivo: str
    estado: Literal["completo", "parcial", "no_disponible"]
    hallazgos: list[HallazgoEstatico]
    herramientas: list[EstadoHerramienta]
    mensaje: str | None = None


class EntradaEstaticaInvalida(ValueError):
    """La entrada no cumple los límites de CODEGUARD."""


def _validar(codigo: str, archivo: str) -> tuple[str, str]:
    if not isinstance(codigo, str) or not codigo.strip() or "\x00" in codigo:
        raise EntradaEstaticaInvalida("El código debe contener texto Python válido.")
    if len(codigo) > MAX_CHARS:
        raise EntradaEstaticaInvalida("El código supera 12.000 caracteres.")
    # Nombre seguro y estable; no se permite que la entrada controle rutas.
    if not isinstance(archivo, str) or len(archivo) > 255 or not archivo.endswith(".py"):
        raise EntradaEstaticaInvalida("El nombre debe ser una ruta Python relativa segura.")
    partes = archivo.split("/")
    if (
        not partes or any(p in ("", ".", "..") or not _SAFE_PART.fullmatch(p) for p in partes)
        or PurePosixPath(archivo).is_absolute()
    ):
        raise EntradaEstaticaInvalida("El nombre debe ser una ruta Python relativa segura.")
    return codigo, archivo


def _ejecutar(comando: list[str], *, entrada: str | None = None, cwd: str) -> tuple[str, str | None]:
    """Acota stdout + stderr durante la lectura; nunca publica stderr."""
    try:
        return _capturar_acotado(
            comando, entrada=entrada, cwd=cwd, env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
                "HOME": cwd,
                "XDG_CACHE_HOME": cwd,
                "RUFF_CACHE_DIR": cwd,
            },
        )
    except FileNotFoundError:
        return "no_disponible", None
    except (OSError, ValueError):
        return "error", None


def _capturar_acotado(
    comando: list[str], *, entrada: str | None, cwd: str, env: dict[str, str],
) -> tuple[str, str | None]:
    """Drena ambas tuberías sin acumular más de MAX_STDOUT bytes entre ellas.

    Los lectores retienen como máximo un bloque adicional cada uno. El límite
    no es una cuota de memoria del analizador ni del JSON ya deserializado.
    """
    with tempfile.TemporaryFile() as datos_entrada:
        if entrada is not None:
            datos_entrada.write(entrada.encode("utf-8"))
            datos_entrada.seek(0)
        proceso = subprocess.Popen(
            comando, stdin=datos_entrada if entrada is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
            cwd=cwd, env=env, shell=False,  # nosec B603 - argv interno; sin shell.
        )
        salidas = [bytearray(), bytearray()]
        bloqueo = threading.Lock()
        fallo = threading.Event()
        total = 0

        def detener() -> None:
            try:
                proceso.kill()
            except OSError:
                pass  # Puede haber terminado entre poll/lectura y kill.

        def leer(tuberia, destino: bytearray) -> None:
            nonlocal total
            try:
                while bloque := tuberia.read(_READ_CHUNK):
                    with bloqueo:
                        if total + len(bloque) > MAX_STDOUT:
                            fallo.set()
                        elif not fallo.is_set():
                            destino.extend(bloque)
                            total += len(bloque)
                    if fallo.is_set():
                        detener()
                        return
            except (OSError, ValueError):
                fallo.set()
                detener()
            finally:
                tuberia.close()

        lectores = [
            threading.Thread(target=leer, args=(tuberia, salida), daemon=True)
            for tuberia, salida in zip((proceso.stdout, proceso.stderr), salidas)
        ]
        limite = time.monotonic() + TOOL_TIMEOUT
        timeout = False
        try:
            for lector in lectores:
                lector.start()
            try:
                proceso.wait(timeout=max(0, limite - time.monotonic()))
                for lector in lectores:
                    lector.join(timeout=max(0, limite - time.monotonic()))
                timeout = any(lector.is_alive() for lector in lectores)
            except subprocess.TimeoutExpired:
                timeout = True
        finally:
            if proceso.poll() is None or timeout:
                detener()
            proceso.wait()  # Recolectar el hijo incluso en exceso de salida/timeout.
            for lector in lectores:
                if lector.ident is not None:
                    lector.join(timeout=0.5)

        if timeout:
            return "timeout", None
        if fallo.is_set() or proceso.returncode not in (0, 1):
            return "error", None
        stdout = salidas[0].decode("utf-8", errors="replace")
        # Detectar módulos ausentes sin publicar su stderr ni su contenido.
        if proceso.returncode == 1 and b"No module named" in salidas[1] and not stdout.strip():
            return "no_disponible", None
        return "ok", stdout


def _texto(valor: object, limite: int = 400) -> str:
    if not isinstance(valor, str):
        return ""
    return valor.replace("\x00", "").strip()[:limite]


def _ruff(salida: str, total_lineas: int) -> list[HallazgoEstatico]:
    try:
        datos = json.loads(salida)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("JSON inválido de Ruff") from None
    if not isinstance(datos, list) or len(datos) > 200:
        raise ValueError("Esquema inesperado de Ruff")
    encontrados: list[HallazgoEstatico] = []
    for item in datos:
        if not isinstance(item, dict):
            raise ValueError("Elemento Ruff inválido")
        regla = _texto(item.get("code"), 40)
        lugar = item.get("location")
        if not isinstance(lugar, dict):
            raise ValueError("Ubicación Ruff inválida")
        linea = lugar.get("row")
        columna = lugar.get("column")
        if not (isinstance(linea, int) and not isinstance(linea, bool) and 1 <= linea <= total_lineas):
            raise ValueError("Línea Ruff fuera de rango")
        if not (isinstance(columna, int) and not isinstance(columna, bool) and columna >= 1):
            columna = None
        if not regla:
            raise ValueError("Regla Ruff vacía")
        mensaje = _texto(item.get("message"))
        encontrados.append(HallazgoEstatico(
            herramienta="ruff", regla=regla, tipo="calidad",
            linea=linea, columna=columna, severidad="baja",
            titulo=f"Ruff {regla}", descripcion=mensaje or "Observación de calidad Python.",
            referencia=None,
        ))
    return encontrados


def _bandit(salida: str, total_lineas: int) -> list[HallazgoEstatico]:
    try:
        datos = json.loads(salida)
    except (json.JSONDecodeError, TypeError):
        raise ValueError("JSON inválido de Bandit") from None
    if not isinstance(datos, dict) or not isinstance(datos.get("results"), list):
        raise ValueError("Esquema inesperado de Bandit")
    resultados = datos["results"]
    if len(resultados) > 200:
        raise ValueError("Demasiados hallazgos Bandit")
    encontrados: list[HallazgoEstatico] = []
    for item in resultados:
        if not isinstance(item, dict):
            raise ValueError("Elemento Bandit inválido")
        linea = item.get("line_number")
        if not (isinstance(linea, int) and not isinstance(linea, bool) and 1 <= linea <= total_lineas):
            raise ValueError("Línea Bandit fuera de rango")
        regla = _texto(item.get("test_id"), 40)
        if not regla:
            raise ValueError("Regla Bandit vacía")
        severidad = _SEVERIDADES.get(_texto(item.get("issue_severity")).upper(), "baja")
        confianza = _SEVERIDADES.get(_texto(item.get("issue_confidence")).upper(), "baja")
        encontrado = HallazgoEstatico(
            herramienta="bandit", regla=regla, tipo="seguridad",
            linea=linea, columna=None, severidad=severidad,
            titulo=f"Bandit {regla}: {_texto(item.get('test_name'), 100)}",
            descripcion=_texto(item.get("issue_text")) or "Posible patrón de seguridad.",
            confianza=confianza,
            referencia=_texto(item.get("more_info"), 300) or None,
        )
        encontrados.append(encontrado)
    return encontrados


def analizar_estatico(codigo: str, archivo: str = "codigo.py") -> ResultadoEstatico:
    """Ejecuta cada herramienta por separado y conserva su estado real."""
    codigo, archivo = _validar(codigo, archivo)
    total_lineas = len(codigo.splitlines())
    estados: list[EstadoHerramienta] = []
    encontrados: list[HallazgoEstatico] = []
    with tempfile.TemporaryDirectory(prefix="codeguard-static-") as directorio:
        # No usar el archivo proporcionado como ruta ni ejecutarlo en Python.
        # Bandit necesita una ruta; Ruff recibe stdin.
        ruta = Path(directorio) / "codigo.py"
        ruta.write_text(codigo, encoding="utf-8")
        planes = [
            ("ruff", [sys.executable, "-m", "ruff", "check", "--isolated",
                      "--select", "E4,E7,E9,F", "--output-format", "json",
                      "--stdin-filename", "codigo.py", "-"], codigo, _ruff),
            ("bandit", [sys.executable, "-m", "bandit", "-f", "json", "-q",
                        str(ruta)], None, _bandit),
        ]
        for nombre, comando, entrada, parser in planes:
            estado, stdout = _ejecutar(comando, entrada=entrada, cwd=directorio)
            hallazgos: list[HallazgoEstatico] = []
            if estado == "ok":
                try:
                    hallazgos = parser(stdout or "", total_lineas)
                except (ValueError, TypeError):
                    estado = "error"
            estados.append(EstadoHerramienta(
                herramienta=nombre, estado=estado, hallazgos=len(hallazgos)
            ))
            encontrados.extend(hallazgos)

    # Se conserva el origen de cada observación, no se inventan citas RAG.
    # Dos alertas de herramientas distintas NO se fusionan sin una equivalencia
    # normativa verificable entre sus reglas.
    encontrados.sort(key=lambda a: (a.linea, a.herramienta, a.regla))
    correctos = sum(e.estado == "ok" for e in estados)
    return ResultadoEstatico(
        archivo=archivo,
        estado="completo" if correctos == 2 else ("parcial" if correctos else "no_disponible"),
        herramientas=estados,
        hallazgos=encontrados,
        mensaje=None if correctos == 2 else "Uno o más analizadores no pudieron completar la revisión.",
    )

