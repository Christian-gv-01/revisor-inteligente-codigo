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



def test_puede_seleccionar_varios_hallazgos(cliente, monkeypatch):
    codigo = "a = 1\nb = 2\nc = 3\nd = 4\n"
    propuesto = "a = 10\nb = 2\nc = 30\nd = 4\n"
    monkeypatch.setattr(correcciones, "_generar_codigo_propuesto", lambda *_: propuesto)
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json={
        "archivo": "varios.py", "codigo_original": codigo, "sha256_original": sha(codigo),
        "objetivos": [{"linea": 1, "descripcion": "Modificar a"},
                       {"linea": 3, "descripcion": "Modificar c"}],
        "lineas_excluidas": [2, 4],
    })
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["codigo_propuesto"] == propuesto


def test_rechaza_modificaciones_de_un_hallazgo_no_seleccionado(cliente, monkeypatch):
    codigo = "a = 1\nb = 2\nc = 3\nd = 4\n"
    propuesto = "a = 10\nb = 20\nc = 30\nd = 40\n"
    monkeypatch.setattr(correcciones, "_generar_codigo_propuesto", lambda *_: propuesto)
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json={
        "archivo": "varios.py", "codigo_original": codigo, "sha256_original": sha(codigo),
        "objetivos": [{"linea": 1, "descripcion": "Modificar a"}],
        "lineas_excluidas": [2, 3, 4],
    })
    assert respuesta.status_code == 502
    assert "zonas no seleccionadas" in respuesta.text
    with sqlite3.connect(correcciones.DB_PATH) as c:
        assert c.execute("SELECT count(*) FROM propuestas_correccion").fetchone()[0] == 0


def test_guardia_con_objetivo_unico_legacy_rechaza_cambios_ajenos(cliente, monkeypatch):
    codigo = "a = 1\nb = 2\nc = 3\nd = 4\n"
    monkeypatch.setattr(correcciones, "_generar_codigo_propuesto",
                        lambda *_: "a = 10\nb = 2\nc = 3\nd = 40\n")
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json={
        "archivo": "ejemplo.py", "codigo_original": codigo, "sha256_original": sha(codigo),
        "objetivo": {"linea": 1, "descripcion": "Modificar a"},
    })
    assert respuesta.status_code == 502


@pytest.mark.parametrize("payload_changes", [
    {"objetivo": {"linea": 3, "descripcion": "duplicado"}, "objetivos": [{"linea": 3, "descripcion": "Revisar"}]},
    {"objetivo": None, "objetivos": []},
    {"objetivo": None, "objetivos": [{"linea": 900, "descripcion": "No existe"}]},
    {"objetivo": None, "objetivos": [{"linea": 3, "descripcion": "Revisar"}], "lineas_excluidas": [3]},
])
def test_entrada_seleccion_de_hallazgos_invalida(cliente, payload_changes):
    payload = payload_previsualizar()
    payload.update(payload_changes)
    if payload_changes.get("objetivos") is not None:
        payload.pop("objetivo", None) if payload_changes.get("objetivo") is None else None
    assert cliente.post("/api/v1/correcciones/previsualizar", json=payload).status_code == 422


# Regression: real model output is a compact patch, not a rewritten full file.
def test_parche_local_eval_con_import_ast_y_original_intacto():
    codigo = (
        "import os\n"
        "\n"
        "def calcular(expresion):\n"
        "    return eval(expresion)\n"
        "\n"
        "def otra_funcion():\n"
        "    return 'NO CAMBIAR'\n"
    )
    parche = {
        "cambios": [{"linea": 4, "antes": "    return eval(expresion)",
                     "despues": "    return ast.literal_eval(expresion)"}],
        "importaciones": ["ast"],
    }
    import json
    correccion = correcciones._aplicar_parche_local(
        codigo, json.dumps(parche), {"linea": 4, "descripcion": "Eliminar eval"},
    )
    assert "import ast\n" in correccion
    assert "    return ast.literal_eval(expresion)\n" in correccion
    assert "    return 'NO CAMBIAR'\n" in correccion
    assert codigo.count("eval(expresion)") == 1
    correcciones._validar_codigo_propuesto(codigo, correccion)
    correcciones._validar_alcance_cambios(codigo, correccion, {4}, {7})


@pytest.mark.parametrize("cambio", [
    {"linea": 6, "antes": "    return 'NO CAMBIAR'", "despues": "    return 'CAMBIADO'"},
    {"linea": 4, "antes": "    return eval(otro)", "despues": "    return 1"},
    {"linea": 4, "antes": "    return eval(expresion)", "despues": "    return 1\n" * 5},
])
def test_parche_local_rechaza_ediciones_no_autorizadas(cambio):
    import json
    codigo = "import os\n\ndef calcular(expresion):\n    return eval(expresion)\n\ndef otra():\n    return 'NO CAMBIAR'\n"
    with pytest.raises(correcciones.CorreccionError) as err:
        correcciones._aplicar_parche_local(
            codigo, json.dumps({"cambios": [cambio], "importaciones": []}),
            {"linea": 4, "descripcion": "Eliminar eval"},
        )
    assert err.value.status_code == 502


def test_parche_local_rechaza_imports_no_autorizados():
    import json
    codigo = "def ejecutar(x):\n    return eval(x)\n"
    with pytest.raises(correcciones.CorreccionError):
        correcciones._aplicar_parche_local(
            codigo, json.dumps({"cambios": [
                {"linea": 2, "antes": "    return eval(x)", "despues": "    return x"}
            ], "importaciones": ["os"]}),
            {"linea": 2, "descripcion": "Corregir"},
        )


def test_contexto_local_no_envia_el_archivo_entero():
    codigo = "\n".join(["clave_privada = 'DATO NO NECESARIO'"] +
                      [f"var_{i} = {i}" for i in range(1, 50)] +
                      ["resultado = eval(entrada)"])
    contexto = correcciones._contexto_local(
        codigo, {"objetivos": [{"linea": 51, "descripcion": "Eval"}]},
    )
    assert len(contexto["lineas_editables"]) <= 2
    assert len(contexto["contexto_no_editable"]) <= 7
    assert "DATO NO NECESARIO" not in str(contexto)
    assert contexto["objetivos"][0]["linea"] == 51


def test_solicitud_v2_permite_mas_de_cien_lineas_excluidas(cliente, monkeypatch):
    codigo = "".join(f"x_{i} = {i}\n" for i in range(1, 120))
    monkeypatch.setattr(correcciones, "_generar_codigo_propuesto",
                        lambda *_: codigo.replace("x_1 = 1", "x_1 = 10"))
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json={
        "archivo": "grande.py", "codigo_original": codigo,
        "sha256_original": sha(codigo),
        "objetivos": [{"linea": 1, "descripcion": "Modificar"}],
        "lineas_excluidas": list(range(2, 120)),
    })
    assert respuesta.status_code == 200, respuesta.text


def test_previsualizacion_multiseleccion_informa_hallazgos_no_modificados(cliente):
    solicitud = {
        "archivo": "usuarios.py",
        "codigo_original": CODIGO_ORIGINAL,
        "sha256_original": sha(CODIGO_ORIGINAL),
        "objetivos": [
            {"linea": 1, "descripcion": "Revisar importación"},
            {"linea": 3, "descripcion": "Parametrizar consulta"},
        ],
    }
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json=solicitud)
    assert respuesta.status_code == 200, respuesta.text
    propuesta = respuesta.json()
    assert propuesta["codigo_propuesto"] == CODIGO_PROPUESTO
    parcial = [v for v in propuesta["advertencias"] if v.startswith("Corrección parcial:")]
    assert len(parcial) == 1
    assert "1 de 2" in parcial[0]
    assert "líneas 1" in parcial[0]


def test_previsualizacion_multiseleccion_completa_no_alega_parcial(cliente):
    solicitud = {
        "archivo": "usuarios.py",
        "codigo_original": CODIGO_ORIGINAL,
        "sha256_original": sha(CODIGO_ORIGINAL),
        "objetivos": [
            {"linea": 3, "descripcion": "Parametrizar consulta"},
            {"linea": 4, "descripcion": "Revisar llamada"},
        ],
    }
    respuesta = cliente.post("/api/v1/correcciones/previsualizar", json=solicitud)
    assert respuesta.status_code == 200, respuesta.text
    assert not any(
        v.startswith("Corrección parcial:")
        for v in respuesta.json()["advertencias"]
    )
