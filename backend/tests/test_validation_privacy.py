"""Regresiones de privacidad en respuestas de validación HTTP 422."""
from fastapi.testclient import TestClient
from app.main import app


def test_422_sin_body_no_expone_input():
    with TestClient(app) as client:
        respuesta = client.post(
            "/api/v1/analizar",
            headers={"Content-Type": "application/json"},
            content="",
        )
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert isinstance(cuerpo["detail"], list)
    for error in cuerpo["detail"]:
        assert set(error).issubset({"type", "loc", "msg"})
        assert "input" not in error
        assert "ctx" not in error


def test_422_codigo_excesivo_no_refleja_marcador():
    marca = "MARCADOR_PRIVADO_FICTICIO_NO_REFLEJAR_12345"
    with TestClient(app) as client:
        respuesta = client.post(
            "/api/v1/analizar",
            json={"archivo": "archivo.py", "codigo": marca + "A" * 12001},
        )
    assert respuesta.status_code == 422
    assert marca not in respuesta.text
    assert '"input"' not in respuesta.text
    assert '"ctx"' not in respuesta.text
