"""Pruebas del contrato de corrección con confirmación humana."""

import hashlib
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.correcciones import router
from app.services import correcciones


CODIGO_ORIGINAL = (
    "import sqlite3\n"
    "nombre = input('Nombre: ')\n"
    "consulta = \"SELECT * FROM usuarios WHERE nombre = '\" + nombre + \"'\"\n"
    "print(consulta)\n"
)
CODIGO_PROPUESTO = (
    "import sqlite3\n"
    "nombre = input('Nombre: ')\n"
    "consulta = 'SELECT * FROM usuarios WHERE nombre = ?'\n"
    "print(consulta, (nombre,))\n"
)


def sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


@pytest.fixture
def cliente(monkeypatch, tmp_path):
    monkeypatch.setattr(
        correcciones,
        "DB_PATH",
        tmp_path / "correcciones_test.sqlite3",
    )
    monkeypatch.setattr(
        correcciones,
        "_generar_codigo_propuesto",
        lambda codigo, objetivo: CODIGO_PROPUESTO,
    )
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def payload_previsualizar():
    return {
        "archivo": "usuarios.py",
        "codigo_original": CODIGO_ORIGINAL,
        "sha256_original": sha(CODIGO_ORIGINAL),
        "objetivo": {
            "linea": 3,
            "descripcion": "Parametrizar la consulta SQL.",
        },
    }


def payload_decision(previsualizacion, decision):
    return {
        "decision": decision,
        "sha256_original": previsualizacion["sha256_original"],
        "sha256_propuesto": previsualizacion["sha256_propuesto"],
    }


def crear_propuesta(cliente):
    respuesta = cliente.post(
        "/api/v1/correcciones/previsualizar",
        json=payload_previsualizar(),
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_previsualizacion_respeta_contrato_y_hashes(cliente):
    resultado = crear_propuesta(cliente)

    assert resultado["version"] == "1"
    assert resultado["estado"] == "pendiente_confirmacion"
    assert resultado["accion"] == "descargar_copia"
    assert resultado["archivo_original"] == "usuarios.py"
    assert resultado["archivo_salida"] == "usuarios.corregido.py"
    assert resultado["codigo_propuesto"] == CODIGO_PROPUESTO
    assert resultado["sha256_original"] == sha(CODIGO_ORIGINAL)
    assert resultado["sha256_propuesto"] == sha(CODIGO_PROPUESTO)
    assert len(resultado["advertencias"]) <= 10
    assert resultado["propuesta_id"]


def test_rechaza_hash_original_incorrecto(cliente):
    payload = payload_previsualizar()
    payload["sha256_original"] = "0" * 64

    respuesta = cliente.post(
        "/api/v1/correcciones/previsualizar",
        json=payload,
    )

    assert respuesta.status_code == 409


def test_aprobar_devuelve_exactamente_el_codigo_previsualizado(cliente):
    propuesta = crear_propuesta(cliente)
    respuesta = cliente.post(
        f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision",
        json=payload_decision(propuesta, "aprobar"),
    )

    assert respuesta.status_code == 200
    data = respuesta.json()
    assert data["estado"] == "aprobada"
    assert data["contenido"] == propuesta["codigo_propuesto"]
    assert data["sha256_contenido"] == propuesta["sha256_propuesto"]
    assert data["archivo_salida"] == "usuarios.corregido.py"
    assert data["tipo_contenido"] == "text/x-python; charset=utf-8"


def test_aprobar_es_idempotente(cliente):
    propuesta = crear_propuesta(cliente)
    url = f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision"
    payload = payload_decision(propuesta, "aprobar")

    primera = cliente.post(url, json=payload)
    segunda = cliente.post(url, json=payload)

    assert primera.status_code == segunda.status_code == 200
    assert primera.json() == segunda.json()


def test_decision_contraria_a_estado_terminal_devuelve_409(cliente):
    propuesta = crear_propuesta(cliente)
    url = f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision"

    aprobacion = cliente.post(
        url,
        json=payload_decision(propuesta, "aprobar"),
    )
    rechazo = cliente.post(
        url,
        json=payload_decision(propuesta, "rechazar"),
    )

    assert aprobacion.status_code == 200
    assert rechazo.status_code == 409


def test_rechazar_no_devuelve_contenido(cliente):
    propuesta = crear_propuesta(cliente)
    respuesta = cliente.post(
        f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision",
        json=payload_decision(propuesta, "rechazar"),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "version": "1",
        "propuesta_id": propuesta["propuesta_id"],
        "estado": "rechazada",
    }
    assert "contenido" not in respuesta.json()


def test_rechazo_es_idempotente(cliente):
    propuesta = crear_propuesta(cliente)
    url = f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision"
    payload = payload_decision(propuesta, "rechazar")

    primera = cliente.post(url, json=payload)
    segunda = cliente.post(url, json=payload)

    assert primera.status_code == segunda.status_code == 200
    assert primera.json() == segunda.json()


def test_hash_de_decision_incorrecto_devuelve_409(cliente):
    propuesta = crear_propuesta(cliente)
    payload = payload_decision(propuesta, "aprobar")
    payload["sha256_propuesto"] = "0" * 64

    respuesta = cliente.post(
        f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision",
        json=payload,
    )

    assert respuesta.status_code == 409


def test_propuesta_caducada_devuelve_410(cliente, monkeypatch):
    propuesta = crear_propuesta(cliente)
    conexion = sqlite3.connect(correcciones.DB_PATH)
    conexion.execute(
        """
        UPDATE propuestas_correccion
        SET caduca_en = 1
        WHERE id_hash = ?
        """,
        (correcciones._id_hash(propuesta["propuesta_id"]),),
    )
    conexion.commit()
    conexion.close()

    respuesta = cliente.post(
        f"/api/v1/correcciones/{propuesta['propuesta_id']}/decision",
        json=payload_decision(propuesta, "aprobar"),
    )

    assert respuesta.status_code == 410


def test_id_inexistente_devuelve_404(cliente):
    respuesta = cliente.post(
        "/api/v1/correcciones/id-inexistente/decision",
        json={
            "decision": "aprobar",
            "sha256_original": "a" * 64,
            "sha256_propuesto": "b" * 64,
        },
    )

    assert respuesta.status_code == 404


def test_no_acepta_nombre_de_archivo_con_ruta(cliente):
    payload = payload_previsualizar()
    payload["archivo"] = "../usuarios.py"

    respuesta = cliente.post(
        "/api/v1/correcciones/previsualizar",
        json=payload,
    )

    assert respuesta.status_code == 422


def test_no_acepta_propuesta_python_invalida(cliente, monkeypatch):
    monkeypatch.setattr(
        correcciones,
        "_generar_codigo_propuesto",
        lambda codigo, objetivo: "Esto no es Python",
    )

    respuesta = cliente.post(
        "/api/v1/correcciones/previsualizar",
        json=payload_previsualizar(),
    )

    assert respuesta.status_code == 502


def test_limite_de_utf16_es_igual_al_frontend(cliente):
    payload = payload_previsualizar()
    payload["codigo_original"] = "a" * 11999 + "😀"
    payload["sha256_original"] = sha(payload["codigo_original"])

    respuesta = cliente.post(
        "/api/v1/correcciones/previsualizar",
        json=payload,
    )

    assert respuesta.status_code == 422


def test_previsualizar_no_crea_archivo_python_en_servidor(cliente, tmp_path):
    crear_propuesta(cliente)

    assert list(tmp_path.glob("*.py")) == []
