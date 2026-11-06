"""Pruebas del evaluador; respuestas HTTP sintéticas, sin Gemini ni Railway."""
import copy
import json
from pathlib import Path

import httpx
import pytest

from comparar_rutas import CONFIG_PUBLICA, Presupuesto, evaluar, guardar, interpretar, main, plan, resumen, validar_config
from run_eval import DEFAULT_DATA, load_cases


def informe(caso, estado="analizado", hallazgos=None):
    return {"archivo": caso["archivo"], "estado": estado, "hallazgos": hallazgos or [], "fuentes": []}


def agente(caso, estado="analizado", modo="gemini_real"):
    return {"archivo": caso["archivo"], "modo": modo, "informe": informe(caso, estado),
            "pasos": [{"numero": 1, "herramienta": "inspeccionar_estructura"}],
            "decisiones": [{"estado": "finalizar", "herramienta": "finalizar"}]}


def hallazgo_sql():
    return {"linea": 2, "severidad": "alta", "categoria": "SQL", "titulo": "Consulta concatenada",
            "explicacion": "Caso controlado", "correccion_sugerida": "Parametrizar", "referencias": ["sql"]}


def respuesta_sql(caso):
    return {**informe(caso, hallazgos=[hallazgo_sql()]),
            "fuentes": [{"id": "sql", "documento": "fixture", "seccion": "SQL", "fuente": "fixture", "url": "https://example.invalid"}]}


def test_plan_congela_cuarenta_solicitudes_y_balancea_orden():
    casos = load_cases(DEFAULT_DATA)
    secuencia = plan(casos)
    assert len(secuencia) == 40
    assert [r for _, r in secuencia[::2]].count("directa") == 10
    for n, caso in enumerate(casos):
        par = secuencia[2 * n:2 * n + 2]
        assert {r for _, r in par} == {"directa", "agente"}
        assert all(c == caso for c, _ in par)


def test_transporte_recibe_mismo_codigo_cuarenta_veces_sin_calidad_inventada():
    casos = load_cases(DEFAULT_DATA)
    por_archivo = {c["archivo"]: c for c in casos}
    recibidos = []
    def responder(req):
        payload = json.loads(req.content)
        caso = por_archivo[payload["archivo"]]
        assert payload["codigo"] == caso["codigo"]
        es_agente = "/agente/" in req.url.path
        assert payload.get("max_pasos") == (3 if es_agente else None)
        recibidos.append((caso["id"], es_agente))
        # Ningún positivo es detectado por este stub: el evaluador NO debe
        # confundir que HTTP funcione con veinte casos correctos.
        return httpx.Response(200, json=agente(caso) if es_agente else informe(caso))
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = evaluar(cliente, casos)
    s = resumen(filas, casos)
    assert len(recibidos) == 40 and s["pares_completos"] == 20
    for ruta in ("directa", "agente"):
        q = s["rutas"][ruta]
        assert q["calidad_solo_completos"]["fn"] == 12
        assert q["calidad_solo_completos"]["f1"] == 0
        assert q["aciertos_sobre_total"] < 1


def test_parcial_conserva_hallazgo_sin_contarlo_como_informe_completo():
    caso = load_cases(DEFAULT_DATA)[0]
    respuesta = respuesta_sql(caso)
    respuesta["estado"] = "parcial"
    original = copy.deepcopy(respuesta)
    datos = interpretar(caso, "directa", respuesta)
    assert respuesta == original
    assert datos["estado_ejecucion"] == "parcial"
    assert datos["metricas_observadas"]["tp"] == 1
    assert not datos["metricas_observadas"]["acierto_caso"]


def test_fallos_no_se_reintentan_y_comparacion_usa_cohorte_comun():
    casos = load_cases(DEFAULT_DATA)[:2]
    contador = 0
    def responder(req):
        nonlocal contador
        contador += 1
        datos = json.loads(req.content)
        caso = next(c for c in casos if c["archivo"] == datos["archivo"])
        if "/agente/" in req.url.path and caso["id"] == casos[1]["id"]:
            return httpx.Response(429, json={"detail": "CUERPO_NO_DEBE_GUARDARSE"})
        r = respuesta_sql(caso)
        return httpx.Response(200, json={**agente(caso), "informe": r} if "/agente/" in req.url.path else r)
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = evaluar(cliente, casos)
    s = resumen(filas, casos)
    assert contador == 4
    assert s["ids_pares_completos"] == [casos[0]["id"]]
    assert s["ids_excluidos_de_comparacion_pareada"] == [casos[1]["id"]]
    assert s["rutas"]["agente"]["tasa_completitud"] == .5
    assert "CUERPO_NO_DEBE_GUARDARSE" not in json.dumps(filas)
    assert "respuesta" not in next(f for f in filas if f.get("http_status") == 429)


@pytest.mark.parametrize("error", ["json", "contrato", "timeout"])
def test_registra_errores_sin_interrumpir_la_segunda_ruta(error):
    caso = load_cases(DEFAULT_DATA)[0]
    def responder(req):
        if "/agente/" in req.url.path:
            return httpx.Response(200, json=agente(caso))
        if error == "timeout":
            raise httpx.ReadTimeout("No copiar detalle privado del transporte")
        if error == "json":
            return httpx.Response(200, text="no JSON")
        return httpx.Response(200, json={"archivo": "otro.py"})
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = evaluar(cliente, [caso])
    assert len(filas) == 2 and filas[1]["estado_ejecucion"] == "completo"
    assert filas[0]["estado_ejecucion"].startswith("error_")
    assert "privado" not in json.dumps(filas)


def test_degradado_exige_parcial_y_cuenta_finalizacion_real():
    caso = load_cases(DEFAULT_DATA)[0]
    with pytest.raises(ValueError):
        interpretar(caso, "agente", agente(caso, modo="degradado"))
    datos = interpretar(caso, "agente", agente(caso, "parcial", "degradado"))
    assert datos["estado_ejecucion"] == "parcial"
    assert datos["finalizacion_temprana"]


def test_sin_completos_no_hay_f1_perfecto():
    caso = load_cases(DEFAULT_DATA)[0]
    filas = [{"id": caso["id"], "ruta": r, "estado_ejecucion": "error_http", "duracion_http_ms": 1} for r in ("directa", "agente")]
    s = resumen(filas, [caso])
    assert s["pares_completos"] == 0
    assert s["calidad_en_mismos_pares_completos"]["agente"]["f1"] is None
    with pytest.raises(ValueError):
        resumen(filas + [filas[0]], [caso])


def test_presupuesto_distingue_pesos_y_espera_sin_superar_diez():
    ahora = [0.0]
    p = Presupuesto(reloj=lambda: ahora[0], dormir=lambda segundos: ahora.__setitem__(0, ahora[0] + segundos))
    assert [p.reservar(w) for w in [3, 3, 3, 1]] == [0, 0, 0, 0]
    assert p.reservar(3) == 61000
    with pytest.raises(ValueError):
        p.reservar(11)


def test_guardado_identifica_pares_parciales_y_no_observa_tokens(tmp_path):
    caso = load_cases(DEFAULT_DATA)[0]
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(lambda req: httpx.Response(503))) as cliente:
        filas = evaluar(cliente, [caso])
    r = {"revision_servidor_declarada": "a" * 40, "casos": filas, "resumen": resumen(filas, [caso]), "llamadas_gemini_observadas": None}
    guardar(tmp_path, r)
    assert "No calculable" in (tmp_path / "comparacion.md").read_text()
    assert json.loads((tmp_path / "resultados.json").read_text())["llamadas_gemini_observadas"] is None
    assert len((tmp_path / "resultados.csv").read_text(encoding="utf-8-sig").splitlines()) == 3


def test_modo_predeterminado_solo_valida_sin_red(monkeypatch, capsys):
    monkeypatch.setattr(httpx, "Client", lambda **_: pytest.fail("No debe acceder a la red"))
    assert main([]) == 0
    assert json.loads(capsys.readouterr().out)["llamadas_realizadas"] == 0


def test_configuracion_no_acepta_credenciales_ni_marcadores():
    campos = CONFIG_PUBLICA - {"fuente_verificacion", "campos_no_verificados"}
    config = {**dict.fromkeys(campos), "campos_no_verificados": sorted(campos), "fuente_verificacion": "No se expone en este fixture"}
    assert validar_config(config) == config
    with pytest.raises(ValueError):
        validar_config({**config, "GEMINI_API_KEY": "MARCADOR_FICTICIO"})
    config["modelo"] = "VALOR_VERIFICADO"
    config["campos_no_verificados"].remove("modelo")
    with pytest.raises(ValueError):
        validar_config(config)
    config["modelo"] = None
    with pytest.raises(ValueError):
        validar_config(config)
