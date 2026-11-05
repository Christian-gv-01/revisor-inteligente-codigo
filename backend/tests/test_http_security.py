"""Pruebas de entrada HTTP: IP no confiable, concurrencia y errores seguros."""
from starlette.requests import Request
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.services.http_security import (
    ControlConcurrencia,
    identidad_cliente,
)


def request_con_ip(peer="192.0.2.15", x_real_ip=None):
    headers = []
    if x_real_ip is not None:
        headers.append((b"x-real-ip", x_real_ip.encode("ascii")))
    return Request({
        "type": "http",
        "method": "POST",
        "path": "/api/v1/analizar",
        "headers": headers,
        "query_string": b"",
        "client": (peer, 1234),
        "server": ("testserver", 80),
        "scheme": "http",
    })


def test_por_defecto_ignora_x_real_ip_suplantada():
    request = request_con_ip("192.0.2.15", "203.0.113.44")
    assert identidad_cliente(request) == "192.0.2.15"


def test_proxy_publico_explicitamente_autorizado():
    request = request_con_ip("192.0.2.15", "203.0.113.44")
    assert identidad_cliente(request, confiar_railway_publico=True) == "203.0.113.44"


@pytest.mark.parametrize("falsa", [
    "1.2.3.4, 5.6.7.8",
    "1.2.3.4:8080",
    "no-es-una-ip",
    "127.0.0.1  ",
])
def test_proxy_rechaza_cabeceras_no_validas(falsa):
    request = request_con_ip("192.0.2.15", falsa)
    # Los espacios exteriores válidos se recortan, no implican una IP falsa.
    resultado = identidad_cliente(request, confiar_railway_publico=True)
    if falsa == "127.0.0.1  ":
        assert resultado == "127.0.0.1"
    else:
        assert resultado == "192.0.2.15"


def test_proxy_admite_ipv6():
    request = request_con_ip("192.0.2.15", "2001:db8::1")
    assert identidad_cliente(request, confiar_railway_publico=True) == "2001:db8::1"


def test_concurrencia_reserva_y_libera():
    limite = ControlConcurrencia(max_activas=2)
    assert limite.adquirir()
    assert limite.adquirir()
    assert limite.activas == 2
    assert not limite.adquirir()
    limite.liberar()
    assert limite.adquirir()
    limite.liberar()
    limite.liberar()
    assert limite.activas == 0


def test_concurrencia_no_libera_sin_reserva():
    limite = ControlConcurrencia(max_activas=1)
    with pytest.raises(RuntimeError):
        limite.liberar()


def test_concurrencia_http_devuelve_503_y_retry_after(monkeypatch):
    import app.main as principal

    limite = ControlConcurrencia(max_activas=1)
    assert limite.adquirir()
    monkeypatch.setattr(principal, "control_concurrencia", limite)
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    with TestClient(app) as client:
        respuesta = client.post(
            "/api/v1/agente/analizar",
            json={},
        )
        assert respuesta.status_code == 503
        assert respuesta.json() == {
            "detail": "Servicio ocupado. Reintenta más tarde."
        }
        assert respuesta.headers["retry-after"] == "3"
        assert respuesta.headers["cache-control"] == "no-store"
    limite.liberar()
    assert limite.activas == 0


def test_concurrencia_se_libera_tras_respuesta_invalida(monkeypatch):
    import app.main as principal

    limite = ControlConcurrencia(max_activas=1)
    monkeypatch.setattr(principal, "control_concurrencia", limite)
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "1")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    with TestClient(app) as client:
        assert client.post("/api/v1/agente/analizar", json={}).status_code == 422
        assert limite.activas == 0
        assert client.post("/api/v1/agente/analizar", json={}).status_code == 422
        assert limite.activas == 0


def test_health_ignora_limite_de_concurrencia(monkeypatch):
    import app.main as principal

    limite = ControlConcurrencia(max_activas=1)
    assert limite.adquirir()
    monkeypatch.setattr(principal, "control_concurrencia", limite)
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "1")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
    limite.liberar()
