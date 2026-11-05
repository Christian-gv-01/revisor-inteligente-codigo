"""Evita falsos aprobados y fugas de datos en la evidencia QA."""
import importlib.util
import sys
from pathlib import Path

import httpx
import pytest

def cargar(nombre):
    ruta = Path(__file__).resolve().parents[1] / "scripts" / f"{nombre}.py"
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo

runner = cargar("pruebas_produccion")
persistencia = cargar("verificar_persistencia_citas")

@pytest.mark.parametrize("datos", [{"detail": "SECRETO"}, {"modo": "SECRETO"}, {"status": "SECRETO"}])
def test_evidencia_no_guarda_respuesta_sensible(datos):
    with httpx.Client() as cliente:
        resultado = runner.ejecutar(cliente, "QA", "errores", "prueba", "400",
            lambda _: httpx.Response(500, json=datos), lambda _: False)
    assert "SECRETO" not in str(resultado)
    assert not resultado.aprobado

def test_evidencia_no_guarda_mensaje_excepcion():
    def fallar(_):
        raise RuntimeError("SECRETO")
    resultado = runner.ejecutar(None, "QA", "errores", "prueba", "200", fallar, lambda _: True)
    assert not resultado.aprobado and "SECRETO" not in str(resultado)

@pytest.mark.parametrize("antes,despues,esperado", [(["a"], ["a"], True), (["a","b"], ["a"], False), ([], [], False)])
def test_citas_no_certifican_volumen(antes, despues, esperado):
    r = persistencia.comparar({"objetivo":"https://demo", "fuentes_ids":antes}, {"objetivo":"https://demo", "fuentes_ids":despues})
    assert r["continuidad_citas"] is esperado
    assert not r["persistencia_volumen_verificada"]

def test_no_compara_instancias_distintas():
    with pytest.raises(ValueError):
        persistencia.comparar({"objetivo":"local"}, {"objetivo":"publico"})


def test_previsualizacion_agente_reserva_presupuesto_publico():
    with runner.ClienteQA(base_url="https://qa.invalid", transport=httpx.MockTransport(lambda _: httpx.Response(200))) as cliente:
        cliente.post("/api/v1/agente/previsualizar", json={})
        assert sum(peso for _, peso in cliente.reservas) == 1


def test_seleccion_solo_ejecuta_los_casos_solicitados():
    rutas = []
    def responder(request):
        rutas.append(request.url.path)
        return httpx.Response(200, json={"status":"ok"})
    with runner.ClienteQA(base_url="http://127.0.0.1", transport=httpx.MockTransport(responder)) as cliente:
        resultados = runner.casos(cliente, {"P01"})
    assert rutas == ["/health"]
    assert [resultado.id for resultado in resultados] == ["P01"]
    assert resultados[0].aprobado
