"""Contrato v2 del agente: decisiones con consecuencias, sin IA externa."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

import app.main as api
from app.models.analisis import InformeModelo
from app.services import agente, llm, rag, presupuesto
from app.services.static_analysis import ResultadoEstatico

CODIGO = "usuario = input()\nconsulta = 'SELECT ' + usuario\ncursor.execute(consulta)\n"
FUENTE = {"id": "seguridad_python-002", "texto": "Usar consultas SQL parametrizadas.",
    "area": "seguridad", "documento": "seguridad_python.md", "seccion": "Regla 2",
    "fuente": "OWASP", "url": "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", "distancia": 0.1}


def solicitud(max_pasos=3, **kw):
    return agente.SolicitudAgente(archivo="ejemplo.py", codigo=CODIGO, max_pasos=max_pasos,
        version_herramientas="2", **kw)


def estatico(codigo, archivo):
    return ResultadoEstatico(archivo=archivo, estado="completo", hallazgos=[], herramientas=[])


@pytest.fixture
def servicios(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    monkeypatch.setenv("GEMINI_API_KEY", "fixture-local")
    monkeypatch.setattr(agente, "analizar_estatico", estatico)
    buscar = Mock(return_value=[FUENTE.copy()])
    monkeypatch.setattr(rag, "buscar_fragmentos", buscar)
    return buscar


@pytest.mark.parametrize("herramienta,argumentos", [
    ("ampliar_contexto", {"linea": 2}),
    ("buscar_referencia", {"categoria": "inyeccion_sql"}),
])
def test_resultado_entra_en_siguiente_decision_y_sintesis(servicios, monkeypatch, herramienta, argumentos):
    vistos = []
    evidencia_final = []
    def elegir(codigo, pasos):
        vistos.append(pasos)
        if len(pasos) == 1:
            return {"herramienta": herramienta, "motivo": "Obtener evidencia", "argumentos": argumentos}
        assert pasos[-1].herramienta == herramienta
        assert pasos[-1].resultado
        return {"herramienta": "finalizar", "motivo": "Evidencia reunida", "argumentos": {}}
    def sintetizar(codigo, *, evidencia):
        evidencia_final.append(evidencia.model_dump())
        return InformeModelo(hallazgos=[])
    monkeypatch.setattr(llm, "analizar_codigo", sintetizar)
    r = agente.ejecutar_agente(solicitud(), planificador=elegir)
    assert len(vistos) == 2 and len(r.pasos) == 2
    assert r.decisiones[0].argumentos.model_dump() == argumentos
    assert r.pasos[1].argumentos.model_dump() == argumentos
    assert r.terminacion == "finalizacion_anticipada"
    if herramienta == "ampliar_contexto":
        assert evidencia_final[0]["contextos_ampliados"][0]["linea_objetivo"] == 2
    else:
        assert evidencia_final[0]["referencias_buscadas"][0]["fragmentos"][0]["id"] == FUENTE["id"]


def test_dos_herramientas_comparten_tres_pasos_y_una_sintesis(servicios, monkeypatch):
    decisiones = iter([
        {"herramienta": "ampliar_contexto", "motivo": "Ver línea", "argumentos": {"linea": 2}},
        {"herramienta": "buscar_referencia", "motivo": "Respaldar SQL", "argumentos": {"categoria": "inyeccion_sql"}},
    ])
    evidencia_final = []
    def sintetizar(codigo, *, evidencia):
        evidencia_final.append(evidencia)
        return InformeModelo(hallazgos=[])
    monkeypatch.setattr(llm, "analizar_codigo", sintetizar)
    r = agente.ejecutar_agente(solicitud(), planificador=lambda c, p: next(decisiones))
    assert len(r.pasos) == 3 and len(r.decisiones) == 2
    assert len(evidencia_final) == 1
    assert evidencia_final[0].contextos_ampliados and evidencia_final[0].referencias_buscadas
    assert r.terminacion == "max_pasos"


def test_finalizacion_temprana_no_llama_herramientas_extra(servicios, monkeypatch):
    elegir = Mock(return_value={"herramienta": "finalizar", "motivo": "No necesito más inspecciones", "argumentos": {}})
    sintesis = Mock(return_value=InformeModelo(hallazgos=[]))
    monkeypatch.setattr(llm, "analizar_codigo", sintesis)
    r = agente.ejecutar_agente(solicitud(), planificador=elegir)
    assert len(r.pasos) == 1 and len(r.decisiones) == 1
    elegir.assert_called_once()
    sintesis.assert_called_once()
    servicios.assert_not_called()
    assert r.terminacion == "finalizacion_anticipada"


def test_max_un_paso_no_planifica(servicios, monkeypatch):
    elegir = Mock(side_effect=AssertionError("No hay presupuesto para decisiones"))
    monkeypatch.setattr(llm, "analizar_codigo", Mock(return_value=InformeModelo(hallazgos=[])))
    r = agente.ejecutar_agente(solicitud(1), planificador=elegir)
    elegir.assert_not_called()
    assert r.terminacion == "max_pasos" and len(r.pasos) == 1


@pytest.mark.parametrize("argumentos", [{}, {"linea": True}, {"linea": "2"}, {"linea": 2.0},
    {"linea": 0}, {"linea": 12001}, {"linea": 2, "url": "https://evil.invalid"}])
def test_argumentos_linea_invalidos_rechazados(argumentos):
    with pytest.raises(ValidationError):
        agente.DecisionAgente(herramienta="ampliar_contexto", motivo="Prueba", argumentos=argumentos)


@pytest.mark.parametrize("herramienta,argumentos", [
    ("buscar_referencia", {}), ("buscar_referencia", {"categoria": "https://evil.invalid"}),
    ("buscar_referencia", {"categoria": "inyeccion_sql", "url": "https://evil.invalid"}),
    ("finalizar", {"linea": 1}), ("detectar_llamadas_sensibles", {"categoria": "rutas"}),
])
def test_argumentos_no_corresponden_a_herramienta(herramienta, argumentos):
    with pytest.raises(ValidationError):
        agente.DecisionAgente(herramienta=herramienta, motivo="Prueba", argumentos=argumentos)


def test_linea_fuera_del_codigo_conserva_traza_de_error(servicios):
    with pytest.raises(agente.ErrorAgenteConTraza) as exc:
        agente.ejecutar_agente(solicitud(), planificador=lambda c, p: {
            "herramienta": "ampliar_contexto", "motivo": "Ver línea", "argumentos": {"linea": 20}})
    assert len(exc.value.pasos) == 1
    assert exc.value.fase == "herramienta"
    assert exc.value.decisiones[-1].estado == "error"


def test_repetir_mismos_argumentos_no_repite_busqueda(servicios, monkeypatch):
    monkeypatch.setattr(llm, "analizar_codigo", Mock(return_value=InformeModelo(hallazgos=[])))
    r = agente.ejecutar_agente(solicitud(), planificador=lambda c, p: {
        "herramienta": "buscar_referencia", "motivo": "Buscar SQL", "argumentos": {"categoria": "inyeccion_sql"}})
    assert len(r.pasos) == 2 and r.decisiones[-1].estado == "repetida"
    assert r.terminacion == "herramienta_repetida"
    servicios.assert_called_once()


@pytest.mark.parametrize("id_fuente", ["seguridad_python-002", "cwe-89-documentado"])
def test_fuentes_buscadas_son_citables_en_sintesis_real(servicios, monkeypatch, id_fuente):
    servicios.return_value = [{**FUENTE, "id": id_fuente}]
    datos = iter([
        {"herramienta": "buscar_referencia", "motivo": "Respaldar SQL", "argumentos": {"categoria": "inyeccion_sql"}},
        {"herramienta": "finalizar", "motivo": "Sintetizar", "argumentos": {}},
    ])
    cliente = Mock()
    cliente.models.generate_content.return_value = SimpleNamespace(text=json.dumps({"hallazgos": [{
        "linea": 2, "severidad": "alta", "categoria": "Inyección SQL", "titulo": "Consulta dinámica",
        "explicacion": "Separar datos de consulta", "correccion_sugerida": "Parametrizar",
        "referencias": [id_fuente], "fragmento_codigo": "consulta = 'SELECT ' + usuario"}]}), usage_metadata=None)
    monkeypatch.setattr(llm.genai, "Client", Mock(return_value=cliente))
    r = agente.ejecutar_agente(solicitud(), planificador=lambda c, p: next(datos))
    assert r.informe.estado_validado == "analizado" and len(r.informe.hallazgos) == 1
    assert r.informe.fuentes[0]["id"] == id_fuente
    enviado = cliente.models.generate_content.call_args.kwargs["contents"].split("DATOS_NO_CONFIABLES_JSON:\n", 1)[1]
    datos_enviados = json.loads(enviado)
    assert FUENTE["texto"] in datos_enviados["contexto_rag_no_confiable"]
    assert datos_enviados["evidencia_herramientas_no_confiable"]["referencias_buscadas"]
    servicios.assert_called_once()


def test_contrato_v1_no_habilita_herramientas_nuevas(servicios):
    with pytest.raises(agente.ErrorAgenteConTraza):
        agente.ejecutar_agente(agente.SolicitudAgente(archivo="ejemplo.py", codigo=CODIGO),
            planificador=lambda c, p: {"herramienta":"buscar_referencia", "motivo":"Buscar", "argumentos":{"categoria":"inyeccion_sql"}})
    servicios.assert_not_called()


def test_http_v2_traza_y_terminacion_y_v1_compatible(servicios, monkeypatch):
    monkeypatch.setattr(agente, "planificar_gemini", lambda c, p, **kw: agente.DecisionAgente(herramienta="finalizar", motivo="Evidencia suficiente"))
    monkeypatch.setattr(llm, "analizar_codigo", Mock(return_value=InformeModelo(hallazgos=[])))
    with TestClient(api.app) as cliente:
        v2 = cliente.post("/api/v1/agente/analizar", json=solicitud().model_dump())
        v1 = cliente.post("/api/v1/agente/analizar", json={"archivo":"ejemplo.py", "codigo":CODIGO})
    assert v2.status_code == 200 and v1.status_code == 200
    assert v2.json()["version_herramientas"] == "2"
    assert v2.json()["terminacion"] == "finalizacion_anticipada"
    assert "version_herramientas" not in v1.json() and "terminacion" not in v1.json()


def configurar_proveedor(monkeypatch, decisiones):
    cliente = Mock()
    cliente.models.generate_content.side_effect = [SimpleNamespace(text=json.dumps(d), usage_metadata=None) for d in decisiones]
    monkeypatch.setattr(llm.genai, "Client", Mock(return_value=cliente))
    return cliente


@pytest.mark.parametrize("temprana", [True, False])
def test_llamadas_reales_acotadas_y_finalizacion_ahorra_decision(servicios, monkeypatch, temprana):
    decisiones = ([{"herramienta":"finalizar", "motivo":"Suficiente", "argumentos":{}}] if temprana else [
        {"herramienta":"ampliar_contexto", "motivo":"Contexto", "argumentos":{"linea":2}},
        {"herramienta":"buscar_referencia", "motivo":"Referencias", "argumentos":{"categoria":"inyeccion_sql"}},
    ])
    proveedor = configurar_proveedor(monkeypatch, decisiones + [{"hallazgos":[]}])
    monkeypatch.setattr(llm, "_recuperar_contexto_rag", lambda c: ("Referencia", [FUENTE]))
    with presupuesto.presupuesto_solicitud(150, 9) as gasto:
        r = agente.ejecutar_agente(solicitud())
    assert gasto.llamadas == (2 if temprana else 3)
    assert proveedor.models.generate_content.call_count == gasto.llamadas
    assert proveedor.close.call_count == gasto.llamadas
    assert len(r.pasos) == (1 if temprana else 3)


def test_limite_de_llamadas_se_conserva_entre_decisiones_y_sintesis(servicios, monkeypatch):
    proveedor = configurar_proveedor(monkeypatch, [
        {"herramienta":"ampliar_contexto", "motivo":"Contexto", "argumentos":{"linea":2}},
        {"herramienta":"buscar_referencia", "motivo":"Referencias", "argumentos":{"categoria":"inyeccion_sql"}},
        {"hallazgos":[]},
    ])
    with presupuesto.presupuesto_solicitud(150, 2), pytest.raises(agente.ErrorAgenteConTraza) as exc:
        agente.ejecutar_agente(solicitud())
    assert exc.value.fase == "informe"
    assert len(exc.value.pasos) == 3 and len(exc.value.decisiones) == 2
    assert proveedor.models.generate_content.call_count == 2


def test_rag_herramienta_agota_plazo_sin_sintesis_ni_llamada_extra(servicios, monkeypatch):
    reloj = [0.0]
    monkeypatch.setattr(presupuesto, "monotonic", lambda: reloj[0])
    def recuperar(*args, **kw):
        reloj[0] = 151
        return [FUENTE]
    servicios.side_effect = recuperar
    proveedor = configurar_proveedor(monkeypatch, [
        {"herramienta":"buscar_referencia", "motivo":"Referencias", "argumentos":{"categoria":"inyeccion_sql"}},
        {"hallazgos":[]},
    ])
    with presupuesto.presupuesto_solicitud(150, 9), pytest.raises(agente.ErrorAgenteConTraza) as exc:
        agente.ejecutar_agente(solicitud())
    assert exc.value.codigo == 504 and exc.value.fase == "herramienta"
    assert len(exc.value.pasos) == 1 and exc.value.decisiones[0].estado == "error"
    assert proveedor.models.generate_content.call_count == 1


def test_misma_herramienta_con_argumentos_distintos_ocupa_otro_paso(servicios, monkeypatch):
    lineas = iter([2, 3])
    evidencia_final = []
    def analizar(codigo, *, evidencia):
        evidencia_final.append(evidencia)
        return InformeModelo(hallazgos=[])
    monkeypatch.setattr(llm, "analizar_codigo", analizar)
    r = agente.ejecutar_agente(solicitud(), planificador=lambda c,p: {
        "herramienta":"ampliar_contexto", "motivo":"Ampliar", "argumentos":{"linea":next(lineas)}})
    assert len(r.pasos) == 3
    assert [d.estado for d in r.decisiones] == ["ejecutada", "ejecutada"]
    assert len(evidencia_final[0].contextos_ampliados) == 2


def test_planificador_recibe_resultados_y_argumentos_anteriores(servicios, monkeypatch):
    resultado = agente.ampliar_contexto(CODIGO, {"linea":2}).model_dump()
    paso = agente.PasoAgente(numero=2, herramienta="ampliar_contexto", motivo="Ampliar", resultado=resultado,
        origen="gemini", argumentos={"linea":2})
    proveedor = configurar_proveedor(monkeypatch, [{"herramienta":"finalizar", "motivo":"Suficiente", "argumentos":{}}])
    d = agente.planificar_gemini(CODIGO, [paso], version_herramientas="2")
    assert d.herramienta == "finalizar"
    kw = proveedor.models.generate_content.call_args.kwargs
    datos = json.loads(kw["contents"].split("DATOS_PLANIFICACION_NO_CONFIABLES_JSON:\n", 1)[1])
    assert datos["resultados_previos_no_confiables"][0]["resultado"] == resultado
    assert datos["resultados_previos_no_confiables"][0]["argumentos"] == {"linea":2}
    assert "ampliar_contexto" in kw["config"].response_json_schema["properties"]["herramienta"]["enum"]


@pytest.mark.parametrize("version", ["3", 2, True])
def test_version_invalida_no_contacta_proveedor(servicios, monkeypatch, version):
    proveedor = configurar_proveedor(monkeypatch, [])
    with TestClient(api.app) as cliente:
        r = cliente.post("/api/v1/agente/analizar", json={"archivo":"ejemplo.py", "codigo":CODIGO, "version_herramientas":version})
    assert r.status_code == 422
    proveedor.models.generate_content.assert_not_called()
