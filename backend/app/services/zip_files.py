
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZipFile, BadZipFile, LargeZipFile
import zlib
from fastapi import HTTPException, UploadFile



# ==========================================
# 1. LÍMITES DE SEGURIDAD
# ==========================================

MAX_ZIP_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_BYTES = 20 * 1024 * 1024
MAX_FILES = 100
MAX_PYTHON_FILES = 5
MAX_SINGLE_FILE_BYTES = 1_048_576
MAX_TOTAL_CODE_CHARS = 12_000


# ==========================================
# 2. FUNCIÓN PRINCIPAL
# ==========================================

async def leer_zip_seguro(
    archivo: UploadFile,
) -> list[tuple[str, str]]:
    """
    Lee archivos Python desde un ZIP.

    No ejecuta el código recibido.
    No extrae archivos al disco.
    Valida rutas, tamaños y contenido.
    """

    nombre_zip = archivo.filename or ""

    # Validar extensión del archivo recibido.
    if not nombre_zip.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Se requiere un archivo .zip.",
        )

    # Leer con límite para evitar cargar ZIP enormes.
    contenido = await archivo.read(MAX_ZIP_BYTES + 1)

    if len(contenido) > MAX_ZIP_BYTES:
        raise HTTPException(
            status_code=413,
            detail="ZIP demasiado grande.",
        )

    try:
        with ZipFile(BytesIO(contenido)) as zip_file:

            entradas = zip_file.infolist()

            # Limitar cantidad total de entradas.
            if len(entradas) > MAX_FILES:
                raise HTTPException(
                    status_code=413,
                    detail="Demasiadas entradas en el ZIP.",
                )

            total_bytes = 0
            archivos_python = []
            nombres = set()

            # ==========================================
            # 3. VALIDAR ENTRADAS DEL ZIP
            # ==========================================

            for entrada in entradas:
                nombre = entrada.filename

                ruta = PurePosixPath(nombre.replace("\\", "/"))

                # Bloquear rutas peligrosas.
                if (
                    not nombre
                    or nombre.startswith(("/", "\\"))
                    or "\\" in nombre
                    or ":" in nombre
                    or ruta.is_absolute()
                    or ".." in ruta.parts
                    or nombre in nombres
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Ruta ZIP insegura.",
                    )

                nombres.add(nombre)

                # Detectar enlaces simbólicos y
                # otros tipos de archivo especiales.
                tipo = (
                    entrada.external_attr >> 16
                ) & 0o170000

                if tipo not in (
                    0,
                    0o100000,
                    0o040000,
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Entrada ZIP no permitida.",
                    )

                # Rechazar archivos cifrados.
                if entrada.flag_bits & 1:
                    raise HTTPException(
                        status_code=400,
                        detail="ZIP cifrado no permitido.",
                    )

                # Acumular tamaño descomprimido declarado.
                total_bytes += entrada.file_size

                if total_bytes > MAX_EXTRACTED_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="ZIP descomprimido demasiado grande.",
                    )

                # Seleccionar solamente archivos .py.
                if (
                    not entrada.is_dir()
                    and nombre.lower().endswith(".py")
                ):
                    if entrada.file_size > MAX_SINGLE_FILE_BYTES:
                        raise HTTPException(
                            status_code=413,
                            detail="Archivo Python demasiado grande.",
                        )

                    archivos_python.append(entrada)

            # ==========================================
            # 4. COMPROBAR ARCHIVOS PYTHON
            # ==========================================

            if not archivos_python:
                raise HTTPException(
                    status_code=400,
                    detail="El ZIP no contiene archivos Python.",
                )

            if len(archivos_python) > MAX_PYTHON_FILES:
                raise HTTPException(
                    status_code=413,
                    detail="Máximo 5 archivos Python por ZIP.",
                )

            # ==========================================
            # 5. LEER CÓDIGO DE FORMA LIMITADA
            # ==========================================

            resultado = []
            caracteres = 0

            for entrada in archivos_python:

                # Leer como máximo 1 MiB + 1 byte.
                with zip_file.open(entrada) as f:
                    datos = f.read(MAX_SINGLE_FILE_BYTES + 1)

                if len(datos) > MAX_SINGLE_FILE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="Archivo Python descomprimido demasiado grande.",
                    )

                # Comprobar consistencia con los metadatos.
                if len(datos) != entrada.file_size:
                    raise HTTPException(
                        status_code=400,
                        detail="Tamaño ZIP inconsistente.",
                    )

                # Convertir bytes a texto UTF-8.
                try:
                    codigo = datos.decode("utf-8")

                except UnicodeDecodeError as error:
                    raise HTTPException(
                        status_code=400,
                        detail="Archivo Python sin UTF-8.",
                    ) from error

                # Rechazar bytes nulos.
                if "\x00" in codigo:
                    raise HTTPException(
                        status_code=400,
                        detail="Archivo con bytes nulos.",
                    )

                # Ignorar archivos vacíos.
                if not codigo.strip():
                    continue

                caracteres += len(codigo)

                if caracteres > MAX_TOTAL_CODE_CHARS:
                    raise HTTPException(
                        status_code=413,
                        detail="Código supera el límite del análisis.",
                    )

                # Guardar nombre y contenido.
                resultado.append(
                    (entrada.filename, codigo)
                )

            if not resultado:
                raise HTTPException(
                    status_code=400,
                    detail="No hay código Python válido.",
                )

            return resultado

    
    except (
        BadZipFile,
        LargeZipFile,
        EOFError,
        RuntimeError,
        zlib.error,
    ) as error:
        raise HTTPException(
            status_code=400,
            detail="Archivo ZIP inválido o no compatible.",
        ) from error

