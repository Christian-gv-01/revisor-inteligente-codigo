"""Intentos y plazo compartido sin red ni esperas reales."""
from datetime import datetime, timezone
from email.utils import format_datetime
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from google.genai import errors, types

from app.services import presupuesto as p


class Reloj:
    def __init__(self):
        self.ahora = 0.0
        self.esperas = []

    def __call__(self):
        return self.ahora

    def dormir(self, segundos):
        self.esperas.append(segundos)
        self.ahora += segundos


@pytest.fixture
def reloj(monkeypatch):
    r = Reloj()
    monkeypatch.setattr(p, "monotonic", r)
    monkeypatch.setattr(p, "sleep", r.dormir)
    monkeypatch.setattr(p, "time", lambda: 1000.0)
    return r


def error(codigo=429, espera=None):
    response = httpx.Response(codigo, headers={} if espera is None else {"Retry-After": espera})
    return errors.APIError(codigo, {"message": "Datos privados del proveedor"}, response)


def generar(cliente):
    return p.generar_con_presupuesto(cliente, model="fixture", contents="Texto no confiable",
        config=types.GenerateContentConfig(temperature=0), timeout_ms=60000)


def cliente(*resultados):
    c = Mock()
    c.models.generate_content.side_effect = resultados
    return c


def test_429_espera_y_reintenta_sin_retry_oculto(reloj):
    c = cliente(error(), "ok")
    with p.presupuesto_solicitud(10, 3):
        assert generar(c) == "ok"
    assert reloj.esperas == [0.6]
    configs = [v.kwargs["config"].http_options for v in c.models.generate_content.call_args_list]
    assert [v.retry_options.attempts for v in configs] == [1, 1]
    assert [v.timeout for v in configs] == [10000, 9400]


def test_agotamiento_preserva_429_del_proveedor(reloj):
    c = cliente(error(), error(), "no debe llamarse")
    with p.presupuesto_solicitud(10, 3), pytest.raises(errors.APIError) as exc:
        generar(c)
    assert exc.value.code == 429
    assert c.models.generate_content.call_count == 2
    assert reloj.esperas == [0.6]


@pytest.mark.parametrize("cabecera,esperado", [("2", 2.0), ("invalido", 0.6), ("-5", 0.6), ("NaN", 0.6)])
def test_retry_after_validado(reloj, cabecera, esperado):
    c = cliente(error(espera=cabecera), "ok")
    with p.presupuesto_solicitud(10, 3):
        assert generar(c) == "ok"
    assert reloj.esperas == [esperado]


def test_retry_after_fecha(reloj):
    fecha = format_datetime(datetime.fromtimestamp(1003, timezone.utc), usegmt=True)
    c = cliente(error(espera=fecha), "ok")
    with p.presupuesto_solicitud(10, 3):
        assert generar(c) == "ok"
    assert reloj.esperas == [3]


def test_espera_que_no_cabe_no_se_acorta_ni_genera(reloj):
    c = cliente(error(espera="60"), "no")
    with p.presupuesto_solicitud(5, 3), pytest.raises(p.PlazoAgotado):
        generar(c)
    assert c.models.generate_content.call_count == 1
    assert reloj.esperas == []


def test_plazo_compartido_entre_llamadas_y_respuesta_tardia(reloj):
    def lenta(**kwargs):
        reloj.ahora += 4
        return "ok"
    c = Mock()
    c.models.generate_content.side_effect = lenta
    with p.presupuesto_solicitud(5, 3):
        assert generar(c) == "ok"
        with pytest.raises(p.PlazoAgotado):
            generar(c)
    configs = [v.kwargs["config"].http_options.timeout for v in c.models.generate_content.call_args_list]
    assert configs == [5000, 1000]


def test_no_inicia_otra_llamada_tras_plazo(reloj):
    c = cliente("no")
    with p.presupuesto_solicitud(2, 3):
        reloj.ahora = 2
        with pytest.raises(p.PlazoAgotado):
            generar(c)
    c.models.generate_content.assert_not_called()


def test_tope_de_consumo_compartido_no_reinicia(reloj):
    c = cliente("ok", "no")
    with p.presupuesto_solicitud(10, 1):
        assert generar(c) == "ok"
        with pytest.raises(p.ConsumoAgotado):
            generar(c)
    assert c.models.generate_content.call_count == 1


@pytest.mark.parametrize("codigo", [400, 401, 403, 404])
def test_errores_no_reintentables_no_esperan(reloj, codigo):
    c = cliente(error(codigo), "no")
    with p.presupuesto_solicitud(10, 3), pytest.raises(errors.APIError):
        generar(c)
    assert c.models.generate_content.call_count == 1
    assert reloj.esperas == []


def test_espera_creciente_acotada(monkeypatch, reloj):
    monkeypatch.setenv("LLM_RETRY_ATTEMPTS", "3")
    c = cliente(error(503), error(503), "ok")
    with p.presupuesto_solicitud(10, 3):
        assert generar(c) == "ok"
    assert reloj.esperas == [0.6, 1.2]


def test_contexto_se_restaura_tras_error(reloj):
    with pytest.raises(RuntimeError), p.presupuesto_solicitud(1, 1):
        raise RuntimeError("fallo")
    with p.presupuesto_solicitud(10, 1):
        assert generar(cliente("ok")) == "ok"


def test_timeout_no_reintenta_para_no_multiplicar_trabajo(reloj):
    c = cliente(httpx.ReadTimeout("Timeout controlado"), "no")
    with p.presupuesto_solicitud(10, 3), pytest.raises(httpx.TimeoutException):
        generar(c)
    assert reloj.esperas == []


def test_sdk_real_no_multiplica_intentos_y_aplica_timeout(reloj):
    from google import genai
    solicitudes = []
    def responder(request):
        solicitudes.append(request)
        if len(solicitudes) == 1:
            return httpx.Response(429, headers={"Retry-After": "1"},
                json={"error": {"code": 429, "message": "fixture", "status": "RESOURCE_EXHAUSTED"}})
        return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": "ok"}]}, "finishReason": "STOP"}]})
    c = genai.Client(api_key="fixture-local", http_options=types.HttpOptions(
        client_args={"transport": httpx.MockTransport(responder)},
        retry_options=types.HttpRetryOptions(attempts=1)))
    try:
        with p.presupuesto_solicitud(5, 3):
            assert generar(c).text == "ok"
    finally:
        c.close()
    assert len(solicitudes) == 2
    assert reloj.esperas == [1]
    assert [r.extensions["timeout"]["read"] for r in solicitudes] == [5, 4]


@pytest.mark.parametrize("variable,ruta,tope", [
    ("ANALYSIS_TOTAL_SECONDS", "/api/v1/analizar", 45),
    ("AGENT_TOTAL_SECONDS", "/api/v1/agente/analizar", 150),
    ("PROJECT_TOTAL_SECONDS", "/api/v1/archivos/zip", 150),
])
def test_configuracion_no_supera_margen_del_cliente(monkeypatch, variable, ruta, tope):
    from app.config import settings
    for valor in ("9999", "NaN", "0", "-1"):
        monkeypatch.setenv(variable, valor)
        assert settings.limites_solicitud(ruta)[0] == tope
    monkeypatch.setenv(variable, "3")
    assert settings.limites_solicitud(ruta)[0] == 3
