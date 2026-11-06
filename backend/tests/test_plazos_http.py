"""Plazos y 429 reales de los adaptadores HTTP, con proveedor/tiempo simulados."""
import hashlib
import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors

import app.main as api
from app.services import presupuesto as p, llm, agente, correcciones, github_repos, static_analysis
from app.services.http_security import ControlConcurrencia
from app.services.rate_limit import LimitadorPonderado
from app.services.static_analysis import ResultadoEstatico


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "fixture-local")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "1")
    monkeypatch.setenv("LLM_RETRY_ATTEMPTS", "2")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "60")
    for nombre in ("ANALYSIS_TOTAL_SECONDS", "AGENT_TOTAL_SECONDS", "PROJECT_TOTAL_SECONDS"):
        monkeypatch.delenv(nombre, raising=False)
    control = ControlConcurrencia(1)
    monkeypatch.setattr(api, "control_concurrencia", control)
    monkeypatch.setattr(correcciones, "DB_PATH", tmp_path / "propuestas.sqlite3")
    reloj = SimpleNamespace(ahora=0.0, esperas=[])
    monkeypatch.setattr(p, "monotonic", lambda: reloj.ahora)
    def dormir(segundos):
        reloj.esperas.append(segundos)
        reloj.ahora += segundos
    monkeypatch.setattr(p, "sleep", dormir)
    fuente = {"id": "seguridad_python-001"}
    monkeypatch.setattr(llm, "_recuperar_contexto_rag", lambda codigo: ("Referencia recuperada", [fuente]))
    monkeypatch.setattr(llm, "_recuperar_contexto_agente", lambda *args: ("Referencia recuperada", [fuente]))
    cliente = Mock()
    cliente.models.generate_content.return_value = SimpleNamespace(text='{"hallazgos": []}', usage_metadata=None)
    monkeypatch.setattr(llm.genai, "Client", Mock(return_value=cliente))
    return reloj, cliente, control


def consulta(cliente):
    return cliente.post("/api/v1/analizar", json={"archivo": "ejemplo.py", "codigo": "x = 1"})


def limitado():
    return errors.APIError(429, {"message": "MARCADOR_PRIVADO_PROVEEDOR"})


def test_429_propio_no_espera_ni_contacta_proveedor(entorno, monkeypatch):
    reloj, proveedor, _ = entorno
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "1")
    limite = LimitadorPonderado(limite_global=1)
    limite.comprobar("otra-persona", 1)
    monkeypatch.setattr(api, "limitador_peticiones", limite)
    with TestClient(api.app) as cliente:
        r = consulta(cliente)
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0
    assert r.headers["Cache-Control"] == "no-store"
    proveedor.models.generate_content.assert_not_called()
    assert reloj.esperas == []


def test_429_proveedor_agotado_es_503_y_libera_concurrencia(entorno, caplog):
    reloj, proveedor, control = entorno
    proveedor.models.generate_content.side_effect = [limitado(), limitado()]
    with TestClient(api.app) as cliente:
        r = consulta(cliente)
    assert r.status_code == 503
    assert "MARCADOR_PRIVADO_PROVEEDOR" not in r.text + caplog.text
    assert reloj.esperas == [0.6]
    assert proveedor.models.generate_content.call_count == 2
    assert control.activas == 0


def test_429_proveedor_se_recupera(entorno):
    reloj, proveedor, control = entorno
    proveedor.models.generate_content.side_effect = [limitado(), SimpleNamespace(text='{"hallazgos": []}', usage_metadata=None)]
    with TestClient(api.app) as cliente:
        assert consulta(cliente).status_code == 200
    assert reloj.esperas == [0.6] and control.activas == 0


def test_presupuesto_no_se_reinicia_por_solicitud_anterior(entorno):
    reloj, proveedor, control = entorno
    def generar(**kwargs):
        assert control.activas == 1
        reloj.ahora += 44
        return SimpleNamespace(text='{"hallazgos": []}', usage_metadata=None)
    proveedor.models.generate_content.side_effect = generar
    with TestClient(api.app) as cliente:
        assert consulta(cliente).status_code == 200
        assert consulta(cliente).status_code == 200
    assert [c.kwargs["config"].http_options.timeout for c in proveedor.models.generate_content.call_args_list] == [45000, 45000]
    assert control.activas == 0


@pytest.mark.parametrize("respaldo", [False, True])
def test_respuesta_tardia_es_504_o_parcial_sin_abandonar_trabajo(entorno, monkeypatch, respaldo):
    reloj, proveedor, control = entorno
    async def estatico(codigo, archivo):
        return ResultadoEstatico(archivo=archivo, estado="completo", hallazgos=[], herramientas=[])
    if respaldo:
        monkeypatch.setattr(api, "_analisis_estatico_si_habilitado", estatico)
    def generar(**kwargs):
        reloj.ahora += 46
        assert control.activas == 1
        return SimpleNamespace(text='{"hallazgos": []}', usage_metadata=None)
    proveedor.models.generate_content.side_effect = generar
    with TestClient(api.app) as cliente:
        r = consulta(cliente)
    assert r.status_code == (200 if respaldo else 504)
    if respaldo:
        assert r.json()["estado"] == "parcial"
        assert r.json()["fuentes"] == []
    assert control.activas == 0


@pytest.mark.parametrize("fuentes", [[], [{"id": "seguridad_python-001"}]])
def test_rag_consume_el_plazo_antes_de_generar(entorno, monkeypatch, fuentes):
    reloj, proveedor, _ = entorno
    def recuperar(codigo):
        reloj.ahora += 46
        return "Referencia" if fuentes else "", fuentes
    monkeypatch.setattr(llm, "_recuperar_contexto_rag", recuperar)
    with TestClient(api.app) as cliente:
        assert consulta(cliente).status_code == 504
    proveedor.models.generate_content.assert_not_called()


def test_agente_comparte_plazo_entre_plan_y_sintesis(entorno, monkeypatch):
    reloj, proveedor, control = entorno
    monkeypatch.setattr(agente, "analizar_estatico", lambda codigo, archivo: ResultadoEstatico(archivo=archivo, estado="completo", hallazgos=[], herramientas=[]))
    def generar(**kwargs):
        reloj.ahora += 80
        texto = '{"herramienta":"finalizar","motivo":"Comprobar informe"}' if kwargs["config"].response_json_schema else '{"hallazgos": []}'
        return SimpleNamespace(text=texto, usage_metadata=None)
    proveedor.models.generate_content.side_effect = generar
    with TestClient(api.app) as cliente:
        r = cliente.post("/api/v1/agente/analizar", json={"archivo": "ejemplo.py", "codigo": "x = 1"})
    assert r.status_code == 200
    assert r.json()["modo"] == "degradado" and r.json()["fase_error"] == "informe"
    assert r.json()["decisiones"][0]["herramienta"] == "finalizar"
    assert control.activas == 0


def test_correccion_tardia_libera_reserva_y_no_publica(entorno):
    reloj, proveedor, control = entorno
    def generar(**kwargs):
        reloj.ahora += 46
        return SimpleNamespace(text="x = 2", candidates=[])
    proveedor.models.generate_content.side_effect = generar
    with TestClient(api.app) as cliente:
        r = cliente.post("/api/v1/correcciones/previsualizar", json={"archivo":"ejemplo.py", "codigo_original":"x = 1",
            "sha256_original":hashlib.sha256(b"x = 1").hexdigest(), "objetivo":{"linea":1,"descripcion":"Revisar"}})
    assert r.status_code == 504 and control.activas == 0
    with sqlite3.connect(correcciones.DB_PATH) as db:
        assert db.execute("SELECT count(*) FROM reservas_correccion").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM propuestas_correccion").fetchone()[0] == 0


def test_github_expirado_no_inicia_red(entorno):
    reloj, _, _ = entorno
    c = Mock()
    with p.presupuesto_solicitud(1, 1):
        reloj.ahora += 2
        with pytest.raises(api.HTTPException) as exc:
            github_repos._leer_json(c, "/repos/demo/ejemplo")
    assert exc.value.status_code == 504
    c.stream.assert_not_called()


def test_estatico_expirado_no_lanza_subproceso(entorno, monkeypatch, tmp_path):
    reloj, _, _ = entorno
    popen = Mock()
    monkeypatch.setattr(static_analysis.subprocess, "Popen", popen)
    with p.presupuesto_solicitud(1, 1):
        reloj.ahora += 2
        assert static_analysis._ejecutar(["no-ejecutar"], cwd=str(tmp_path)) == ("timeout", None)
    popen.assert_not_called()
