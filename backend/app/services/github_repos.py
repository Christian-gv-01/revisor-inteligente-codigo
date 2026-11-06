"""Descarga de código Python de repositorios públicos de GitHub, sin ejecutarlo."""

import base64
import binascii
import json
import re
from urllib.parse import quote, urlsplit

import httpx
from fastapi import HTTPException
from app.services.presupuesto import comprobar_plazo, tiempo_disponible, PlazoAgotado

MAX_ARCHIVOS = 5
MAX_CARACTERES = 12_000
MAX_ARCHIVO_BYTES = 48_000
MAX_RESPUESTA_BYTES = 2_000_000

_PROPIETARIO = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
_REPOSITORIO = re.compile(r"[A-Za-z0-9_.-]{1,100}")
_SHA = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})")


def validar_url_github(url: str) -> tuple[str, str]:
    if not isinstance(url, str) or len(url) > 2048:
        raise HTTPException(400, "URL de GitHub inválida.")

    try:
        parsed = urlsplit(url.strip())
    except ValueError as error:
        raise HTTPException(400, "URL de GitHub inválida.") from error

    if (
        parsed.scheme != "https"
        or parsed.netloc.lower() != "github.com"
        or parsed.query
        or parsed.fragment
    ):
        raise HTTPException(400, "Utiliza una URL HTTPS de github.com sin parámetros.")

    partes = parsed.path.strip("/").split("/")
    if (
        len(partes) != 2
        or not _PROPIETARIO.fullmatch(partes[0])
        or not _REPOSITORIO.fullmatch(partes[1])
        or partes[1] in (".", "..")
    ):
        raise HTTPException(400, "La URL debe tener la forma github.com/usuario/repositorio.")

    return partes[0], partes[1]


def _leer_json(client: httpx.Client, ruta: str, limite: int = MAX_RESPUESTA_BYTES) -> dict:
    try:
        restante = tiempo_disponible(10.0)
        client.timeout = httpx.Timeout(restante, connect=min(5.0, restante))
        with client.stream("GET", ruta) as response:
            estado = response.status_code
            if estado == 404:
                raise HTTPException(404, "Repositorio o recurso público no encontrado.")
            if estado in (403, 429):
                raise HTTPException(503, "GitHub limitó o rechazó la consulta pública.")
            if estado != 200:
                raise HTTPException(502, "GitHub no pudo completar la consulta.")

            datos = bytearray()
            for bloque in response.iter_bytes():
                comprobar_plazo()
                if len(datos) + len(bloque) > limite:
                    raise HTTPException(413, "La respuesta de GitHub supera el límite permitido.")
                datos.extend(bloque)
            comprobar_plazo()
    except (httpx.TimeoutException, PlazoAgotado) as error:
        raise HTTPException(504, "Se agotó el tiempo de espera de GitHub.") from error
    except httpx.RequestError as error:
        raise HTTPException(502, "No se pudo contactar a GitHub.") from error

    try:
        resultado = json.loads(datos)
    except (ValueError, UnicodeDecodeError) as error:
        raise HTTPException(502, "GitHub devolvió una respuesta inválida.") from error

    if not isinstance(resultado, dict):
        raise HTTPException(502, "La respuesta de GitHub tiene un formato inesperado.")
    return resultado


def _sha_valido(valor: object) -> str:
    if not isinstance(valor, str) or not _SHA.fullmatch(valor):
        raise HTTPException(502, "GitHub devolvió un identificador inválido.")
    return valor


def obtener_archivos_python_github(url: str) -> list[tuple[str, str]]:
    """Obtiene archivos .py públicos; solo devuelve nombres y texto UTF-8."""
    propietario, repositorio = validar_url_github(url)
    base = f"/repos/{propietario}/{repositorio}"

    with httpx.Client(
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CODEGUARD-revisor-codigo",
        },
        timeout=httpx.Timeout(10.0, connect=5.0),
        follow_redirects=False,
        trust_env=False,
    ) as client:
        metadata = _leer_json(client, base)
        if metadata.get("private") is not False:
            raise HTTPException(403, "Solo se admiten repositorios públicos.")

        rama = metadata.get("default_branch")
        if not isinstance(rama, str) or not rama or len(rama) > 255:
            raise HTTPException(502, "No se encontró la rama principal del repositorio.")

        commit = _leer_json(client, f"{base}/commits/{quote(rama, safe='')}")
        objeto_commit = commit.get("commit")
        arbol_commit = objeto_commit.get("tree") if isinstance(objeto_commit, dict) else None
        sha_arbol = _sha_valido(arbol_commit.get("sha") if isinstance(arbol_commit, dict) else None)

        arbol = _leer_json(client, f"{base}/git/trees/{sha_arbol}?recursive=1")
        if arbol.get("truncated") is True:
            raise HTTPException(413, "Repositorio demasiado grande para un análisis completo.")

        entradas = arbol.get("tree")
        if not isinstance(entradas, list):
            raise HTTPException(502, "GitHub no devolvió un árbol de archivos válido.")

        candidatos = []
        for entrada in entradas:
            if not isinstance(entrada, dict) or entrada.get("type") != "blob":
                continue
            ruta = entrada.get("path")
            if not isinstance(ruta, str) or not ruta.lower().endswith(".py"):
                continue
            if (
                len(ruta) > 255
                or ruta.startswith("/")
                or "\\" in ruta
                or "\x00" in ruta
                or any(parte in ("", ".", "..") for parte in ruta.split("/"))
            ):
                raise HTTPException(400, "El repositorio contiene una ruta Python inválida.")
            tamano = entrada.get("size")
            if type(tamano) is not int or tamano < 0 or tamano > MAX_ARCHIVO_BYTES:
                raise HTTPException(413, "Un archivo Python supera el límite de 48 KB.")
            sha = _sha_valido(entrada.get("sha"))
            candidatos.append((ruta, sha))

        if not candidatos:
            raise HTTPException(400, "El repositorio no contiene archivos Python.")
        if len(candidatos) > MAX_ARCHIVOS:
            raise HTTPException(413, "El repositorio supera el límite de 5 archivos Python.")

        resultado = []
        total_caracteres = 0
        for ruta, sha in sorted(candidatos):
            blob = _leer_json(client, f"{base}/git/blobs/{sha}", 150_000)
            if blob.get("encoding") != "base64" or not isinstance(blob.get("content"), str):
                raise HTTPException(502, "GitHub devolvió un archivo no compatible.")
            try:
                datos = base64.b64decode("".join(blob["content"].split()), validate=True)
                codigo = datos.decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError) as error:
                raise HTTPException(400, "El repositorio contiene un archivo Python no válido en UTF-8.") from error

            if len(datos) > MAX_ARCHIVO_BYTES or "\x00" in codigo:
                raise HTTPException(413, "Archivo Python demasiado grande o binario.")
            if not codigo.strip():
                continue
            total_caracteres += len(codigo)
            if total_caracteres > MAX_CARACTERES:
                raise HTTPException(413, "El código supera el límite de 12.000 caracteres.")
            resultado.append((ruta, codigo))

        if not resultado:
            raise HTTPException(400, "El repositorio no contiene código Python analizable.")
        return resultado
