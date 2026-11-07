"""Telemetría sintética; sin llamadas de red o proveedor."""
import json

import httpx
import pytest

from comparar_rutas import comprobar_esquema, evaluar, resumen
from consumo_evaluacion import leer_consumo, resumen_consumo, CABECERA_CONSUMO
from run_eval import DEFAULT_DATA, load_cases


def datos(**kw):
    return {"version": 1, "intentos": 1, "respuestas": 1, "tokens_entrada": 10,
            "tokens_salida": 2, "tokens_totales": 12, "uso_completo": True, **kw}


@pytest.mark.parametrize("valor", [None, "no json", "{}", "[]", "x" * 2049,
    json.dumps(datos(tokens_totales=True)), json.dumps(datos(tokens_entrada=-1)),
    json.dumps(datos(intentos=0)), json.dumps(datos(version=True)),
    json.dumps(datos(api_key="DATO_NO_PERMITIDO")),
    json.dumps(datos(intentos=2)), json.dumps(datos(uso_completo=False))])
def test_cabecera_no_fiable_no_se_guarda_como_consumo(valor):
    assert leer_consumo(valor) is None


def test_cobertura_no_convierte_ausentes_ni_reintentos_en_cero():
    filas = [{"consumo_ia": datos()}, {"consumo_ia": datos(intentos=2,
        tokens_entrada=None, tokens_salida=None, tokens_totales=None, uso_completo=False)}]
    s = resumen_consumo(filas)
    assert s["tokens_totales"] is None
    assert s["tokens_totales_suma_solo_conocidos"] == 12
    assert s["tokens_totales_solicitudes_con_dato"] == 1
    assert s["intentos"] == 3
    assert resumen_consumo([{}])["intentos"] is None


def test_cuarenta_solicitudes_cuatro_pasos_y_consumo_en_errores_preservados():
    casos = load_cases(DEFAULT_DATA)
    def responder(req):
        carga = json.loads(req.content)
        if "/agente/" in req.url.path:
            assert carga["max_pasos"] == 4
            return httpx.Response(503, headers={CABECERA_CONSUMO: json.dumps(datos(intentos=2,
                respuestas=1, tokens_entrada=None, tokens_salida=None, tokens_totales=None, uso_completo=False))})
        return httpx.Response(200, json={"archivo": carga["archivo"], "estado": "abstenido",
            "hallazgos": [], "fuentes": []}, headers={CABECERA_CONSUMO: json.dumps(datos())})
    with httpx.Client(base_url="http://fixture.invalid", transport=httpx.MockTransport(responder)) as cliente:
        filas = evaluar(cliente, casos, max_pasos_agente=4)
    s = resumen(filas, casos)
    assert len(filas) == 40
    assert s["rutas"]["directa"]["consumo_ia"]["tokens_totales"] == 240
    assert s["rutas"]["agente"]["consumo_ia"]["tokens_totales"] is None
    assert s["rutas"]["agente"]["consumo_ia"]["intentos"] == 40
    assert s["pares_completos"] == 0


def test_servidor_antiguo_no_recibe_analisis_de_cuatro_pasos():
    esquema = {"paths": {"/api/v1/analizar": {}, "/api/v1/agente/analizar": {"post": {
        "requestBody": {"content": {"application/json": {"schema": {"properties": {
            "version_herramientas": {"enum": ["1", "2"]}, "max_pasos": {"maximum": 3}}}}}}}}}}
    with pytest.raises(ValueError, match="máximo"):
        comprobar_esquema(esquema, max_pasos=4)
