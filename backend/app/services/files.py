
from pathlib import Path

from fastapi import HTTPException, UploadFile

MAX_FILE_BYTES = 1_048_576  # 1 MiB
MAX_CODE_CHARS = 12_000


async def leer_python_seguro(archivo: UploadFile) -> tuple[str, str]:
    """Lee un archivo Python sin guardarlo ni ejecutarlo."""

    nombre = archivo.filename or ""

    if not nombre or Path(nombre).name != nombre:
        raise HTTPException(
            status_code=400,
            detail="Nombre de archivo no válido.",
        )

    if not nombre.lower().endswith(".py"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos .py.",
        )

    # Leer un byte más que el límite para detectar
    # archivos excesivos sin cargarlos completos.
    contenido = await archivo.read(MAX_FILE_BYTES + 1)

    if len(contenido) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="El archivo supera el límite de 1 MiB.",
        )

    try:
        codigo = contenido.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe utilizar codificación UTF-8.",
        ) from error

    if not codigo.strip():
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    if "\x00" in codigo:
        raise HTTPException(
            status_code=400,
            detail="El archivo contiene bytes nulos.",
        )

    if len(codigo) > MAX_CODE_CHARS:
        raise HTTPException(
            status_code=413,
            detail="El código supera los 12000 caracteres permitidos.",
        )

    return nombre, codigo
