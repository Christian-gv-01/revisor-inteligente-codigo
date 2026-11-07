"""Consumo reportado, límites y aislamiento, con SDK simulado."""
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors, types

import app.main as api
from app.models.analisis import InformeModelo
from app.services import presupuesto as p
from app.services.consumo import CABECERA_CONSUMO, ConsumoIA


def respuesta(n=10, uso=True):
    return SimpleNamespace(text="{}", usage_metadata=SimpleNamespace(
        prompt_token_count=n, candidates_token_count=2, total_token_count=n + 2) if uso else None)


def llamar(cliente):
    return p.generar_con_presupuesto(cliente, model="simulado", contents="DATOS_NO_PUBLICAR",
        config=types.GenerateContentConfig(temperature=0), timeout_ms=1000)


def test_agrega_uso_de_dos_respuestas_del_sdk():
    c = Mock()
    c.models.generate_content.side_effect = [respuesta(), respuesta(20)]
    with p.presupuesto_solicitud(10, 3) as actual:
        llamar(c); llamar(c)
    assert actual.consumo.publico() == {"version": 1, "intentos": 2, "respuestas": 2,
        "tokens_entrada": 30, "tokens_salida": 4, "tokens_totales": 34, "uso_completo": True}


@pytest.mark.parametrize("uso", [None, {}, {"prompt_token_count": True}, {"total_token_count": -1}])
def test_metadatos_ausentes_o_invalidos_no_se_inventan(uso):
    c = ConsumoIA(); c.iniciar_intento(); c.registrar_respuesta(SimpleNamespace(usage_metadata=uso))
    assert c.publico()["tokens_entrada"] is None
    assert c.publico()["tokens_totales"] is None
    assert not c.publico()["uso_completo"]


def test_429_y_exito_no_se_convierten_en_consumo_total_conocido(monkeypatch):
    monkeypatch.setattr(p, "sleep", lambda n: None)
    c = Mock(); c.models.generate_content.side_effect = [
        errors.APIError(429, {"message": "NO_PUBLICAR"}, httpx.Response(429)), respuesta()]
    with p.presupuesto_solicitud(10, 3) as actual:
        llamar(c)
    d = actual.consumo.publico()
    assert (d["intentos"], d["respuestas"]) == (2, 1)
    assert d["tokens_totales"] is None and not d["uso_completo"]


def test_respuesta_tardia_conserva_uso_aunque_no_se_acepte_resultado(monkeypatch):
    reloj = [0.0]; monkeypatch.setattr(p, "monotonic", lambda: reloj[0])
    def generar(**kw):
        reloj[0] = 2.0
        return respuesta()
    c = Mock(); c.models.generate_content.side_effect = generar
    with p.presupuesto_solicitud(1, 3) as actual, pytest.raises(p.PlazoAgotado):
        llamar(c)
    assert actual.consumo.publico()["tokens_totales"] == 12


def test_cabecera_http_aislada_entre_dos_solicitudes_concurrentes(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0")
    barrera = Barrier(2)
    def sintetizar(codigo, **kw):
        barrera.wait(timeout=10)
        c = Mock(); c.models.generate_content.return_value = respuesta(10 if codigo == "x=1" else 100)
        llamar(c)
        return InformeModelo(hallazgos=[])
    monkeypatch.setattr(api, "analizar_codigo", sintetizar)
    def enviar(codigo):
        with TestClient(api.app) as cliente:
            r = cliente.post("/api/v1/analizar", json={"archivo": "x.py", "codigo": codigo})
            assert r.status_code == 200
            return json.loads(r.headers[CABECERA_CONSUMO])
    with ThreadPoolExecutor(max_workers=2) as executor:
        a, b = list(executor.map(enviar, ["x=1", "x=2"]))
    assert [a["tokens_totales"], b["tokens_totales"]] == [12, 102]
    assert "DATOS_NO_PUBLICAR" not in json.dumps([a, b])


def test_validacion_http_no_consume_ia_y_lo_indica(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    r = TestClient(api.app).post("/api/v1/agente/analizar", json={})
    assert r.status_code == 422
    assert json.loads(r.headers[CABECERA_CONSUMO])["tokens_totales"] == 0
