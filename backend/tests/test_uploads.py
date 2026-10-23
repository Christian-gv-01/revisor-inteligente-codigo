
from io import BytesIO
from zipfile import ZipFile
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.models.analisis import InformeModelo
from app.services.llm import LLMError


client = TestClient(main_module.app)


def crear_zip(archivos: dict[str, bytes]) -> bytes:
    buffer = BytesIO()

    with ZipFile(buffer, "w") as zip_file:
        for nombre, contenido in archivos.items():
            zip_file.writestr(nombre, contenido)

    return buffer.getvalue()


def configurar_analisis(monkeypatch, error=None):
    if error is None:
        mock = Mock(return_value=InformeModelo(hallazgos=[]))
    else:
        mock = Mock(side_effect=error)

    monkeypatch.setattr(main_module, "analizar_codigo", mock)
    return mock


# PYTHON: carga válida
def test_archivo_python_valido(monkeypatch):
    codigo = "print('hola')"
    mock = configurar_analisis(monkeypatch)

    respuesta = client.post(
        "/api/v1/archivos",
        files={
            "archivo": (
                "ejemplo.py",
                codigo.encode(),
                "text/x-python",
            )
        },
    )

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["archivo"] == "ejemplo.py"
    assert respuesta.json()["estado"] == "analizado"
    mock.assert_called_once_with(codigo)


# PYTHON: entradas inválidas y límites
@pytest.mark.parametrize(
    "nombre, contenido, estado",
    [
        ("ejemplo.txt", b"print('hola')", 400),
        ("../ejemplo.py", b"print('hola')", 400),
        ("ejemplo.py", b"", 400),
        ("ejemplo.py", b"\xff", 400),
        ("ejemplo.py", b"print\x00('hola')", 400),
        ("ejemplo.py", b"a" * 12001, 413),
        ("ejemplo.py", b"a" * (1024 * 1024 + 1), 413),
    ],
    ids=[
        "extension-no-permitida",
        "ruta-insegura",
        "contenido-vacio",
        "utf8-invalido",
        "byte-nulo",
        "codigo-supera-12000",
        "archivo-supera-1-mib",
    ],
)
def test_archivo_python_rechaza_entradas_invalidas(
    monkeypatch, nombre, contenido, estado
):
    mock = configurar_analisis(monkeypatch)

    respuesta = client.post(
        "/api/v1/archivos",
        files={
            "archivo": (
                nombre,
                contenido,
                "application/octet-stream",
            )
        },
    )

    assert respuesta.status_code == estado, respuesta.text
    mock.assert_not_called()


# PYTHON: error controlado del proveedor
def test_archivo_python_controla_error_llm(monkeypatch):
    mock = configurar_analisis(
        monkeypatch,
        LLMError("Proveedor temporalmente no disponible.", 503),
    )

    respuesta = client.post(
        "/api/v1/archivos",
        files={
            "archivo": (
                "ejemplo.py",
                b"print('hola')",
                "text/x-python",
            )
        },
    )

    assert respuesta.status_code == 503
    mock.assert_called_once()


# ZIP: proyecto válido
def test_zip_valido(monkeypatch):
    codigo = "print('hola')"
    contenido = crear_zip(
        {"src/ejemplo.py": codigo.encode("utf-8")}
    )
    mock = configurar_analisis(monkeypatch)

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 200, respuesta.text

    resultado = respuesta.json()
    assert resultado["archivo_zip"] == "proyecto.zip"
    assert resultado["estado"] == "analizado"
    assert resultado["total_archivos"] == 1
    assert resultado["informes"][0]["archivo"] == "src/ejemplo.py"

    mock.assert_called_once_with(codigo)


# ZIP: extensión y estructura
def test_zip_rechaza_extension_incorrecta(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.txt",
                b"contenido",
                "text/plain",
            )
        },
    )

    assert respuesta.status_code == 400
    mock.assert_not_called()


def test_zip_corrupto(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                b"esto no es un ZIP",
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 400
    mock.assert_not_called()


def test_zip_sin_archivos_python(monkeypatch):
    mock = configurar_analisis(monkeypatch)
    contenido = crear_zip({"README.md": b"Documentacion"})

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 400
    mock.assert_not_called()


# ZIP: rutas peligrosas y cantidad de archivos
def test_zip_rechaza_ruta_insegura(monkeypatch):
    mock = configurar_analisis(monkeypatch)
    contenido = crear_zip(
        {"../fuera.py": b"print('hola')"}
    )

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 400
    mock.assert_not_called()


def test_zip_rechaza_mas_de_cinco_archivos_python(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    contenido = crear_zip({
        f"archivo_{i}.py": b"print('hola')"
        for i in range(6)
    })

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 413
    mock.assert_not_called()


# ZIP: contenido inválido y límites acumulados
@pytest.mark.parametrize(
    "nombre, contenido",
    [
        ("mal.py", b"\xff"),
        ("mal.py", b"print\x00('hola')"),
        ("vacio.py", b"   \n"),
    ],
    ids=[
        "utf8-invalido",
        "byte-nulo",
        "codigo-vacio",
    ],
)
def test_zip_rechaza_codigo_python_invalido(
    monkeypatch, nombre, contenido
):
    mock = configurar_analisis(monkeypatch)
    archivo_zip = crear_zip({nombre: contenido})

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                archivo_zip,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 400
    mock.assert_not_called()


def test_zip_rechaza_exceso_de_caracteres_acumulados(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    contenido = crear_zip({
        "uno.py": b"a" * 7000,
        "dos.py": b"b" * 7000,
    })

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 413
    mock.assert_not_called()


def test_zip_rechaza_carga_superior_a_cinco_mib(monkeypatch):
    mock = configurar_analisis(monkeypatch)
    contenido = b"x" * (5 * 1024 * 1024 + 1)

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 413
    mock.assert_not_called()


# ZIP: error controlado del proveedor
def test_zip_controla_error_llm(monkeypatch):
    mock = configurar_analisis(
        monkeypatch,
        LLMError("Proveedor temporalmente no disponible.", 503),
    )

    contenido = crear_zip(
        {"ejemplo.py": b"print('hola')"}
    )

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 503
    mock.assert_called_once()

def test_zip_rechaza_mas_de_cien_entradas(monkeypatch):
    configurar_analisis(monkeypatch)

    contenido = crear_zip({
        f"archivo_{i}.txt": b"x"
        for i in range(101)
    })

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 413
    assert respuesta.json()["detail"] == "Demasiadas entradas en el ZIP."


def test_zip_rechaza_exceso_de_tamano_descomprimido(monkeypatch):
    from zipfile import ZIP_DEFLATED

    configurar_analisis(monkeypatch)

    buffer = BytesIO()

    with ZipFile(
        buffer,
        "w",
        compression=ZIP_DEFLATED,
    ) as zip_file:
        zip_file.writestr(
            "datos.bin",
            b"A" * (20 * 1024 * 1024 + 1),
        )

    contenido = buffer.getvalue()

    # El ZIP comprimido debe caber en el límite de 5 MiB.
    assert len(contenido) < 5 * 1024 * 1024

    respuesta = client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "proyecto.zip",
                contenido,
                "application/zip",
            )
        },
    )

    assert respuesta.status_code == 413
    assert respuesta.json()["detail"] == "ZIP descomprimido demasiado grande."
