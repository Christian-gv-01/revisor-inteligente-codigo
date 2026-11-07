"""El presupuesto aprobado no debe ocultar consumo ni ampliar el límite exterior."""
import io
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import Mock
from zipfile import ZipFile

from fastapi.testclient import TestClient
from google.genai import types
import pytest

import app.main as api
from app.models.analisis import RespuestaAnalisis
from app.services import presupuesto as p, proyectos


def llamada(cliente):
    return p.generar_con_presupuesto(cliente, model="fixture", contents="Sintético",
        config=types.GenerateContentConfig(temperature=0), timeout_ms=1000)


def cliente_sdk():
    c = Mock()
    c.models.generate_content.return_value = SimpleNamespace(text="{}", usage_metadata={
        "prompt_token_count":10,"candidates_token_count":2,"total_token_count":12})
    return c


def test_anidado_conserva_uso_y_reserva_en_el_padre():
    c=cliente_sdk()
    with p.presupuesto_solicitud(10,3) as exterior:
        with p.presupuesto_solicitud(5,2):
            llamada(c);llamada(c)
        assert exterior.llamadas == 2
        assert exterior.consumo.publico()["tokens_totales"] == 24
        llamada(c)
        with pytest.raises(p.ConsumoAgotado):llamada(c)
    assert c.models.generate_content.call_count == 3


def test_dos_hijos_no_reinician_el_limite_global():
    c=cliente_sdk()
    with p.presupuesto_solicitud(10,3):
        with p.presupuesto_solicitud(10,2):llamada(c);llamada(c)
        with p.presupuesto_solicitud(10,2):
            llamada(c)
            with pytest.raises(p.ConsumoAgotado):llamada(c)
    assert c.models.generate_content.call_count == 3


def test_limite_menor_del_hijo_se_conserva_sin_gastar_al_fallar():
    c=cliente_sdk()
    with p.presupuesto_solicitud(10,3) as exterior:
        with p.presupuesto_solicitud(10,1):
            llamada(c)
            with pytest.raises(p.ConsumoAgotado):llamada(c)
        assert exterior.llamadas == 1
        llamada(c)
    assert exterior.consumo.publico()["intentos"] == 2


def test_hijo_no_amplia_el_plazo_del_padre(monkeypatch):
    reloj=[0.0];monkeypatch.setattr(p,"monotonic",lambda:reloj[0])
    c=cliente_sdk()
    with p.presupuesto_solicitud(1,3):
        with p.presupuesto_solicitud(100,3):
            reloj[0]=2.0
            with pytest.raises(p.PlazoAgotado):llamada(c)
    c.models.generate_content.assert_not_called()


def test_hijos_concurrentes_reservan_el_padre_atomicamente():
    exterior=p.Presupuesto(10,3)
    hijos=[p.Presupuesto(10,2,padre=exterior) for _ in range(4)]
    barrera=Barrier(4)
    def reservar(hijo):
        barrera.wait(timeout=5)
        aceptadas=0
        for _ in range(2):
            try:hijo.reservar_intento();aceptadas+=1
            except p.ConsumoAgotado:pass
        return aceptadas
    with ThreadPoolExecutor(max_workers=4) as pool:
        aceptadas=list(pool.map(reservar,hijos))
    assert sum(aceptadas) == exterior.llamadas == sum(h.llamadas for h in hijos) == 3


def test_http_aprobacion_proyecto_publica_uso_del_sdk(monkeypatch,tmp_path):
    monkeypatch.setenv("PROJECT_BUDGET_ENABLED","1")
    monkeypatch.setenv("CORRECTIONS_COOKIE_SECURE","0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED","0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED","0")
    monkeypatch.setattr(proyectos,"DB_PATH",tmp_path/"proyectos.sqlite3")
    sdk=cliente_sdk()
    async def analizar(codigo,archivo,**kw):
        llamada(sdk)
        return RespuestaAnalisis(archivo=archivo,estado="analizado",hallazgos=[])
    monkeypatch.setattr(api,"analizar_con_respaldo",analizar)
    mem=io.BytesIO()
    with ZipFile(mem,"w") as z:z.writestr("uno.py","print(1)\n")
    with TestClient(api.app) as c:
        d=c.post("/api/v1/proyectos/previsualizar/zip",files={"archivo":("uno.zip",mem.getvalue(),"application/zip")}).json()
        r=c.post(f"/api/v1/proyectos/{d['presupuesto_id']}/decision",json={
            "decision":"aprobar","confirmar":True,"sha256_manifiesto":d["sha256_manifiesto"]})
        repetida=c.post(f"/api/v1/proyectos/{d['presupuesto_id']}/decision",json={
            "decision":"aprobar","confirmar":True,"sha256_manifiesto":d["sha256_manifiesto"]})
    assert repetida.status_code == 200 and repetida.json() == r.json()
    assert json.loads(repetida.headers["X-Codeguard-Consumo-IA"])["intentos"] == 0
    assert r.status_code == 200 and r.json()["estado"] == "finalizado"
    uso=json.loads(r.headers["X-Codeguard-Consumo-IA"])
    assert uso["intentos"] == uso["respuestas"] == 1
    assert uso["tokens_totales"] == 12
