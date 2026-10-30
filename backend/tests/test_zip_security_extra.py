
from io import BytesIO
import stat
from unittest.mock import Mock
from zipfile import ZipFile, ZipInfo

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.models.analisis import InformeModelo


client = TestClient(main_module.app)


def crear_zip(archivos):
    buffer = BytesIO()

    with ZipFile(buffer, "w") as zip_file:
        for nombre, contenido in archivos.items():
            # zipfile normaliza las barras invertidas.
            # Por eso escribimos primero la ruta normalizada.
            nombre_zip = nombre.replace("\\", "/")

            zip_file.writestr(
                nombre_zip,
                contenido,
            )

    datos = buffer.getvalue()

    # Restaurar las barras invertidas directamente en
    # las cabeceras ZIP para simular un ZIP malicioso real.
    for nombre in archivos:

        if "\\" not in nombre:
            continue

        nombre_normalizado = nombre.replace(
            "\\", "/"
        ).encode("utf-8")

        nombre_original = nombre.encode("utf-8")

        assert len(nombre_normalizado) == len(nombre_original)

        # El nombre aparece en la cabecera local
        # y en el directorio central del ZIP.
        assert datos.count(nombre_normalizado) >= 2

        datos = datos.replace(
            nombre_normalizado,
            nombre_original,
        )

    return datos


def configurar_analisis(monkeypatch):
    mock = Mock(
        return_value=InformeModelo(hallazgos=[])
    )

    monkeypatch.setattr(
        main_module,
        "analizar_codigo",
        mock,
    )

    return mock


def enviar_zip(contenido):
    return client.post(
        "/api/v1/archivos/zip",
        files={
            "archivo": (
                "prueba.zip",
                contenido,
                "application/zip",
            )
        },
    )


# =========================================================
# 1. RUTAS ABSOLUTAS Y RUTAS WINDOWS
# =========================================================

@pytest.mark.parametrize(
    "nombre",
    [
        "/fuera.py",
        r"carpeta\archivo.py",
        "C:/fuera.py",
    ],
    ids=[
        "ruta-absoluta-unix",
        "ruta-con-barras-invertidas",
        "ruta-unidad-windows",
    ],
)
def test_zip_rechaza_rutas_absolutas_y_windows(
    monkeypatch,
    nombre,
):
    mock = configurar_analisis(monkeypatch)

    contenido = crear_zip({
        nombre: b"print('hola')",
    })

    respuesta = enviar_zip(contenido)

    assert respuesta.status_code == 400
    mock.assert_not_called()


# =========================================================
# 2. ENLACES SIMBÓLICOS
# =========================================================

def test_zip_rechaza_enlaces_simbolicos(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    buffer = BytesIO()

    info = ZipInfo("enlace.py")
    info.create_system = 3

    info.external_attr = (
        stat.S_IFLNK | 0o777
    ) << 16

    with ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(
            info,
            b"archivo_destino.py",
        )

    respuesta = enviar_zip(buffer.getvalue())

    assert respuesta.status_code == 400

    assert respuesta.json()["detail"] == (
        "Entrada ZIP no permitida."
    )

    mock.assert_not_called()


# =========================================================
# 3. ARCHIVOS DUPLICADOS
# =========================================================

def test_zip_rechaza_nombres_duplicados(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    buffer = BytesIO()

    with pytest.warns(UserWarning, match="Duplicate name"):
        with ZipFile(buffer, "w") as zip_file:
            zip_file.writestr(
                "duplicado.py",
                b"print('primero')",
            )

            zip_file.writestr(
                "duplicado.py",
                b"print('segundo')",
            )

    respuesta = enviar_zip(buffer.getvalue())

    assert respuesta.status_code == 400

    assert respuesta.json()["detail"] == (
        "Ruta ZIP insegura."
    )

    mock.assert_not_called()


# =========================================================
# 4. ARCHIVOS ZIP CIFRADOS
# =========================================================

def marcar_zip_como_cifrado(contenido):
    datos = bytearray(contenido)

    firmas = [
        (b"PK\x03\x04", 6),
        (b"PK\x01\x02", 8),
    ]

    for firma, desplazamiento in firmas:
        posicion = 0
        encontrados = 0

        while True:
            posicion = datos.find(
                firma,
                posicion,
            )

            if posicion < 0:
                break

            datos[posicion + desplazamiento] |= 0x01

            posicion += len(firma)
            encontrados += 1

        assert encontrados >= 1

    return bytes(datos)


def test_zip_rechaza_archivos_cifrados(monkeypatch):
    mock = configurar_analisis(monkeypatch)

    contenido = crear_zip({
        "cifrado.py": b"print('hola')",
    })

    contenido_cifrado = marcar_zip_como_cifrado(
        contenido
    )

    respuesta = enviar_zip(contenido_cifrado)

    assert respuesta.status_code == 400

    assert respuesta.json()["detail"] == (
        "ZIP cifrado no permitido."
    )

    mock.assert_not_called()


# =========================================================
# 5. ARCHIVOS PYTHON SUPERIORES A 1 MIB
# =========================================================

def test_zip_rechaza_archivo_python_superior_a_un_mib(
    monkeypatch,
):
    mock = configurar_analisis(monkeypatch)

    contenido = crear_zip({
        "grande.py": b"x" * (1_048_576 + 1),
    })

    respuesta = enviar_zip(contenido)

    assert respuesta.status_code == 413

    assert respuesta.json()["detail"] == (
        "Archivo Python demasiado grande."
    )

    mock.assert_not_called()
