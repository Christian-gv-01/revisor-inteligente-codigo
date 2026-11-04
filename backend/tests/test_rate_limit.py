"""Pruebas sin llamadas reales al proveedor, con reloj controlado."""
from fastapi.testclient import TestClient

from app.main import app
from app.services import rate_limit


def test_limite_por_cliente_y_recuperacion_tras_ventana():
    reloj = [100.0]
    limitador = rate_limit.LimitadorPonderado(
        ventana=60, limite_global=30, limite_cliente=2, reloj=lambda: reloj[0]
    )
    assert limitador.comprobar("1.2.3.4", 1).permitido
    assert limitador.comprobar("1.2.3.4", 1).permitido
    denegado = limitador.comprobar("1.2.3.4", 1)
    assert not denegado.permitido
    assert denegado.retry_after == 60
    reloj[0] += 60
    assert limitador.comprobar("1.2.3.4", 1).permitido


def test_presupuesto_global_compartido():
    limitador = rate_limit.LimitadorPonderado(
        limite_global=5, limite_cliente=5, reloj=lambda: 10.0
    )
    assert limitador.comprobar("cliente-1", 5).permitido
    rechazo = limitador.comprobar("cliente-2", 1)
    assert not rechazo.permitido
    assert rechazo.retry_after == 60


def test_pesos_de_zip_y_repositorios():
    assert rate_limit.ENDPOINT_WEIGHTS["/api/v1/archivos/zip"] == 5
    assert rate_limit.ENDPOINT_WEIGHTS["/api/v1/repositorios/github"] == 5
    assert rate_limit.ENDPOINT_WEIGHTS["/api/v1/agente/analizar"] == 3


def test_rechaza_peso_invalido():
    import pytest

    with pytest.raises(ValueError):
        rate_limit.LimitadorPonderado().comprobar("cliente", 0)


def test_rate_limit_http_429_antes_de_invocar_gemini(monkeypatch):
    import app.main as principal

    limitador = rate_limit.LimitadorPonderado(
        limite_global=1, limite_cliente=1, reloj=lambda: 100.0
    )
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setattr(principal, "limitador_peticiones", limitador)
    # /api/v1/agente/analizar cuesta 3 y se rechaza antes de llegar al agente.
    with TestClient(app) as client:
        respuesta = client.post(
            "/api/v1/agente/analizar",
            json={"archivo": "ejemplo.py", "codigo": "print('hola')"},
        )
    assert respuesta.status_code == 429
    assert respuesta.json() == {
        "detail": "Demasiadas solicitudes. Reintenta más tarde."
    }
    assert respuesta.headers["retry-after"] == "60"
    assert respuesta.headers["cache-control"] == "no-store"


def test_health_no_consume_cupo(monkeypatch):
    import app.main as principal

    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    monkeypatch.setattr(
        principal,
        "limitador_peticiones",
        rate_limit.LimitadorPonderado(
            limite_global=1, limite_cliente=1, reloj=lambda: 100.0
        ),
    )
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health").status_code == 200
