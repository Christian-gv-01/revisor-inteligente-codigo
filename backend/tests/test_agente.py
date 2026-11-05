"""Pruebas del orquestador y HTTP; todos los servicios externos están simulados."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.models.analisis import InformeModelo
from app.services.agente import (
    DecisionAgente, SolicitudAgente, detectar_llamadas_sensibles,
    ejecutar_agente, inspeccion_local, inspeccionar_estructura,
    revisar_consultas_sql,
)
from app.routes.agente import router


def entrada(codigo="dato = input()\neval(dato)\n", pasos=3):
    return SolicitudAgente(archivo="ejemplo.py", codigo=codigo, max_pasos=pasos)


def informe_ficticio(codigo):
    return InformeModelo(hallazgos=[])


def test_limite_pasos():
    with pytest.raises(ValidationError): entrada(pasos=4)
    with pytest.raises(ValidationError): entrada(pasos=0)


def test_limite_caracteres():
    with pytest.raises(ValidationError): entrada(codigo="a" * 12001)


def test_rechaza_traversal():
    with pytest.raises(ValidationError): SolicitudAgente(archivo="../secretos.py", codigo="print(1)")


def test_rechaza_campos_adicionales():
    with pytest.raises(ValidationError): SolicitudAgente(archivo="ejemplo.py", codigo="x=1", comando="rm")


def test_lista_cerrada_tools():
    with pytest.raises(ValidationError): DecisionAgente(herramienta="borrar_archivos", motivo="ilegítimo")


def test_detecta_eval_en_linea_correcta():
    assert {"linea": 2, "llamada": "eval"} in detectar_llamadas_sensibles("x=1\neval(input())\n")["indicadores"]


def test_comentarios_no_son_ejecutados_ni_detectados():
    assert detectar_llamadas_sensibles("# eval(input())\nprint('ok')\n")["indicadores"] == []


def test_detecta_subprocess():
    r = detectar_llamadas_sensibles('import subprocess\nsubprocess.run("echo x", shell=True)\n')
    assert {"linea": 2, "llamada": "subprocess.run"} in r["indicadores"]


def test_sql_dinamico():
    r = revisar_consultas_sql('cursor.execute("SELECT " + name)\n')
    assert r["indicadores"] == [{"linea": 1, "patron": "SQL dinamico (concatenacion)"}]


def test_sql_parametrizado_sin_indicador():
    assert revisar_consultas_sql('cursor.execute("SELECT * FROM t WHERE id = ?", (id,))\n')["indicadores"] == []


def test_sintaxis_invalida_reportada():
    assert inspeccionar_estructura("def :\n")["sintaxis_valida"] is False


def test_agente_usa_evidencia_y_finaliza():
    ejecutadas = []
    def planner(codigo, pasos):
        ejecutadas.append([p.herramienta for p in pasos])
        return DecisionAgente(herramienta="detectar_llamadas_sensibles" if len(pasos) == 1 else "finalizar", motivo="validación")
    seen = []
    def analizar(codigo):
        seen.append(codigo)
        return informe_ficticio(codigo)
    pasos, informe = ejecutar_agente(entrada(), planificador=planner, analizador=analizar)
    assert [p.herramienta for p in pasos] == ["inspeccionar_estructura", "detectar_llamadas_sensibles"]
    assert ejecutadas == [["inspeccionar_estructura"], ["inspeccionar_estructura", "detectar_llamadas_sensibles"]]
    assert seen == [entrada().codigo]
    assert informe.hallazgos == []


def test_repeticiones_se_detienen():
    pasos, _ = ejecutar_agente(entrada(), planificador=lambda c, p: DecisionAgente(herramienta="inspeccionar_estructura", motivo="repetido"), analizador=informe_ficticio)
    assert len(pasos) == 1


def test_max_un_paso_no_llama_planificador():
    def forbidden(*a): raise AssertionError("No llamar Gemini")
    pasos, _ = ejecutar_agente(entrada(pasos=1), planificador=forbidden, analizador=informe_ficticio)
    assert len(pasos) == 1


def test_inspeccion_local_no_depende_de_ia():
    pasos = inspeccion_local(entrada())
    assert len(pasos) == 3
    assert pasos[1].resultado["indicadores"][0]["llamada"] == "eval"


def test_inspeccion_local_rechaza_byte_nulo():
    with pytest.raises(ValueError): inspeccion_local(entrada(codigo="print(1)\x00"))


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_http_local_con_traza():
    r = client.post("/api/v1/agente/previsualizar", json=entrada().model_dump())
    assert r.status_code == 200
    data = r.json()
    assert data["modo"] == "inspeccion_local"
    assert data["informe"]["estado"] == "abstenido"
    assert data["requiere_confirmacion_humana"] is False
    assert len(data["pasos"]) == 3


def test_http_rechaza_ruta_ilegal():
    r = client.post("/api/v1/agente/previsualizar", json={"archivo":"../../x.py", "codigo":"x=1"})
    assert r.status_code == 422


def test_http_real_con_llm_simulado(monkeypatch):
    import app.routes.agente as route_module
    def mock_ejecutar(solicitud):
        return inspeccion_local(solicitud)[:1], informe_ficticio(solicitud.codigo)
    monkeypatch.setattr(route_module, "ejecutar_agente", mock_ejecutar)
    r = client.post("/api/v1/agente/analizar", json=entrada().model_dump())
    assert r.status_code == 200
    assert r.json()["modo"] == "gemini_real"
    assert len(r.json()["pasos"]) == 1


def test_http_rechaza_codigo_vacio():
    r = client.post("/api/v1/agente/analizar", json={"archivo":"x.py", "codigo":"   "})
    assert r.status_code == 422


def test_dashboard_accesible():
    r = client.get("/agente/demo")
    assert r.status_code == 200
    assert "CODEGUARD" in r.text
    assert "/api/v1/agente/analizar" in r.text


def test_no_ejecuta_codigo(tmp_path):
    target = tmp_path / "no_debe_existir.txt"
    codigo = f"open({str(target)!r}, 'w').write('PELIGRO')\n"
    assert inspeccionar_estructura(codigo)["sintaxis_valida"]
    assert not target.exists()


def test_planificador_gemini_configura_reintentos_transitorios(monkeypatch):
    from unittest.mock import Mock
    import app.services.agente as modulo
    from google import genai

    monkeypatch.setenv("GEMINI_API_KEY", "clave-ficticia-de-pruebas")
    cliente_falso = Mock()
    cliente_falso.models.generate_content.return_value.text = (
        '{"herramienta":"finalizar","motivo":"Sin herramientas adicionales."}'
    )
    crear_cliente = Mock(return_value=cliente_falso)
    monkeypatch.setattr(genai, "Client", crear_cliente)

    decision = modulo.planificar_gemini("print('hola')", [])
    assert decision.herramienta == "finalizar"
    http = crear_cliente.call_args.kwargs["http_options"]
    assert http.timeout == 45000
    assert http.retry_options.attempts == 2
    assert http.retry_options.http_status_codes == [502, 503, 504]
    cliente_falso.models.generate_content.assert_called_once()
    cliente_falso.close.assert_called_once()
