"""Contrato del evaluador contra ejemplos publicados; todo sintético, sin red."""
import copy
import json
from pathlib import Path

import httpx
import pytest

import comparar_rutas as c
from contrato_agente_evaluacion import validar_traza
from run_eval import DEFAULT_DATA, load_cases

FIXTURES = Path(__file__).resolve().parents[1] / "docs/contrato-agente-v2"


def leer(nombre):
    return json.loads((FIXTURES / nombre).read_text(encoding="utf-8"))


def caso(nombre="01-solicitud-contexto-y-referencia.json"):
    return {**load_cases(DEFAULT_DATA)[0], **leer(nombre)}


@pytest.mark.parametrize("respuesta,solicitud,estado,terminacion", [
    ("04-respuesta-contexto-y-referencia.json", "01-solicitud-contexto-y-referencia.json", "completo", "max_pasos"),
    ("07-respuesta-finalizacion-anticipada.json", "05-solicitud-finalizacion-anticipada.json", "completo", "finalizacion_anticipada"),
    ("08-respuesta-error-herramienta.json", "01-solicitud-contexto-y-referencia.json", "parcial", None),
])
def test_json_publicados_se_interpretan_sin_cambiar_su_estado(respuesta, solicitud, estado, terminacion):
    r = leer(respuesta)
    original = copy.deepcopy(r)
    fila = c.interpretar(caso(solicitud), "agente", r)
    assert r == original
    assert fila["estado_ejecucion"] == estado
    assert fila["terminacion"] == terminacion
    assert fila["version_herramientas"] == "2"
    if estado == "parcial":
        assert fila["fase_error"] == "herramienta"
        assert fila["decisiones_error"] == 1
        assert not fila["metricas_observadas"]["acierto_caso"]
        assert fila["pasos_respaldo"] == 2


def test_no_se_puede_presentar_v1_como_comparacion_del_producto_v2():
    with pytest.raises(ValueError):
        c.interpretar(caso(), "agente", leer("09-respuesta-v1-compatible.json"))


@pytest.mark.parametrize("alterar", [
    lambda r: r.pop("version_herramientas"),
    lambda r: r.update(version_herramientas="1"),
    lambda r: r.update(max_pasos=True),
    lambda r: r.update(terminacion="finalizacion_anticipada"),
    lambda r: r["decisiones"][0]["argumentos"].update(linea=True),
    lambda r: r["decisiones"][0]["argumentos"].update(consulta="libre"),
    lambda r: r["pasos"][1]["argumentos"].update(linea=1),
    lambda r: r["pasos"][1]["resultado"]["lineas"][0].update(texto="CONTENIDO_CAMBIADO"),
    lambda r: r["pasos"][1]["resultado"].update(linea_inicio=True),
    lambda r: r["pasos"][1]["resultado"]["lineas"][0].update(truncada=0),
    lambda r: r["pasos"][2]["resultado"].update(categoria="rutas"),
    lambda r: r["pasos"][2]["resultado"]["fragmentos"][0].update(url="https://github.com/otro/repo"),
    lambda r: r["pasos"][2]["resultado"]["fragmentos"][0].update(texto="x" * 2001),
    lambda r: r["decisiones"][1].update(estado="error"),
    lambda r: r["pasos"][2].update(origen="local"),
])
def test_rechaza_trazas_alteradas(alterar):
    r = leer("04-respuesta-contexto-y-referencia.json")
    alterar(r)
    with pytest.raises(ValueError):
        validar_traza(caso(), r)


def test_no_cuenta_finalizacion_si_solo_fue_declarada_sin_decision():
    r = leer("07-respuesta-finalizacion-anticipada.json")
    r["decisiones"] = []
    with pytest.raises(ValueError):
        validar_traza(caso("05-solicitud-finalizacion-anticipada.json"), r)


def test_un_error_herramienta_se_conserva_como_parcial_en_el_transporte():
    ejemplo = caso()
    def responder(req):
        return httpx.Response(200, json=leer("08-respuesta-error-herramienta.json") if "/agente/" in req.url.path else leer("04-respuesta-contexto-y-referencia.json")["informe"])
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = c.evaluar(cliente, [ejemplo])
    resumen = c.resumen(filas, [ejemplo])
    assert resumen["pares_completos"] == 0
    assert resumen["rutas"]["agente"]["estados"] == {"parcial": 1}
    assert resumen["rutas"]["agente"]["fases_error"] == {"herramienta": 1}
    assert resumen["rutas"]["agente"]["decisiones_error"] == 1
    assert filas[1]["respuesta"]["decisiones"][0]["estado"] == "error"


def test_latencia_http_no_incluye_calculo_local(monkeypatch):
    reloj = [0.0]
    monkeypatch.setattr(c.time, "perf_counter", lambda: reloj[0])
    interpretar = c.interpretar
    def lenta(*args):
        reloj[0] += 10
        return interpretar(*args)
    monkeypatch.setattr(c, "interpretar", lenta)
    def responder(req):
        reloj[0] += 2
        r = leer("04-respuesta-contexto-y-referencia.json")
        return httpx.Response(200, json=r if "/agente/" in req.url.path else r["informe"])
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = c.evaluar(cliente, [caso()])
    assert [f["duracion_http_ms"] for f in filas] == [2000, 2000]


def esquema(version="2"):
    return {"paths": {c.RUTAS["directa"]: {}, c.RUTAS["agente"]: {"post": {"requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/SolicitudAgente"}}}}}}},
            "components": {"schemas": {"SolicitudAgente": {"properties": {"version_herramientas": {"enum": ["1", version]}}}}}}


def test_esquema_exige_que_el_servidor_anuncie_v2():
    c.comprobar_esquema(esquema())
    with pytest.raises(ValueError):
        c.comprobar_esquema(esquema("1"))


@pytest.mark.parametrize("tipo", ["v1", "fixture"])
def test_preflight_incompatible_no_inicia_analisis(tmp_path, monkeypatch, tipo):
    datos = c.CONFIG_PUBLICA - {"fuente_verificacion", "campos_no_verificados"}
    config = {**dict.fromkeys(datos), "fuente_verificacion": "Fixture de prueba", "campos_no_verificados": sorted(datos)}
    path = tmp_path / "config.json"; path.write_text(json.dumps(config))
    posts = []
    def responder(req):
        if req.method == "POST":
            posts.append(req.url.path)
        if req.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"}, headers={"X-Integration-Provider": "stub"} if tipo == "fixture" else {})
        return httpx.Response(200, json=esquema("1" if tipo == "v1" else "2"))
    original = httpx.Client
    monkeypatch.setattr(c.httpx, "Client", lambda **kw: original(**kw, transport=httpx.MockTransport(responder)))
    with pytest.raises((ValueError, RuntimeError)):
        c.main(["--ejecutar", "--base-url", "http://127.0.0.1", "--revision-servidor", "a" * 40,
                "--dataset-sha256", c.hashlib.sha256(DEFAULT_DATA.read_bytes()).hexdigest(),
                "--config-publica", str(path), "--output", str(tmp_path / "corrida")])
    assert posts == []
    assert not (tmp_path / "corrida").exists()


def test_validacion_de_configuracion_registra_limites_y_no_inventa_default():
    campos = c.CONFIG_PUBLICA - {"fuente_verificacion", "campos_no_verificados"}
    config = {**dict.fromkeys(campos), "campos_no_verificados": sorted(campos), "fuente_verificacion": "No verificada"}
    assert c.validar_config(config)["intentos_llm"] is None
    for campo, valor in [("intentos_llm", 4), ("intentos_llm", True), ("plazo_directo_segundos", 46),
                          ("plazo_agente_segundos", 151), ("distancia_max_rag", 3), ("estatico_directa_habilitado", 1)]:
        candidata = copy.deepcopy(config)
        candidata["campos_no_verificados"].remove(campo)
        candidata[campo] = valor
        with pytest.raises(ValueError):
            c.validar_config(candidata)


def test_linea_booleana_no_puede_contar_como_uno():
    ejemplo = caso()
    respuesta = leer("04-respuesta-contexto-y-referencia.json")["informe"]
    respuesta["hallazgos"][0]["linea"] = True
    with pytest.raises(ValueError):
        c.interpretar(ejemplo, "directa", respuesta)
