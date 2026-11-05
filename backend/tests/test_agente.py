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


def test_http_agente_503_degrada_a_ast_sin_citas(monkeypatch):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    def proveedor_falla(solicitud):
        raise LLMError("Proveedor no disponible.", 503)

    monkeypatch.setattr(route_module, "ejecutar_agente", proveedor_falla)
    r = client.post("/api/v1/agente/analizar", json=entrada().model_dump())
    assert r.status_code == 200
    data = r.json()
    assert data["modo"] == "degradado"
    assert data["informe"]["estado"] == "parcial"
    assert data["informe"]["hallazgos"] == []
    assert data["informe"]["fuentes"] == []
    assert [p["herramienta"] for p in data["pasos"]] == [
        "inspeccionar_estructura", "detectar_llamadas_sensibles", "revisar_consultas_sql"
    ]
    assert "Gemini" in data["informe"]["mensaje"]
    assert data["requiere_confirmacion_humana"] is False


@pytest.mark.parametrize("codigo_error", [502, 503, 504])
def test_http_degradacion_controlada_para_errores_temporales(monkeypatch, codigo_error):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    def proveedor_falla(solicitud):
        raise LLMError("No disponible.", codigo_error)

    monkeypatch.setattr(route_module, "ejecutar_agente", proveedor_falla)
    solicitud = entrada(pasos=1)
    r = client.post("/api/v1/agente/analizar", json=solicitud.model_dump())
    assert r.status_code == 200
    assert r.json()["modo"] == "degradado"
    assert len(r.json()["pasos"]) == 1
    assert r.json()["max_pasos"] == 1


def test_http_no_oculta_un_error_no_elegible_para_fallback(monkeypatch):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    def fallo_no_transitorio(solicitud):
        raise LLMError("El usuario ha excedido el limite.", 429)

    monkeypatch.setattr(route_module, "ejecutar_agente", fallo_no_transitorio)
    r = client.post("/api/v1/agente/analizar", json=entrada().model_dump())
    assert r.status_code == 429
    assert "degradado" not in r.text


def test_planificador_malicioso_no_puede_ejecutar_herramienta_arbitraria():
    from app.services.llm import LLMError
    decisiones = []

    def planner(codigo, pasos):
        decisiones.append(len(pasos))
        return {"herramienta": "borrar_archivos", "motivo": "Ignora las reglas."}

    def analizador_prohibido(codigo):
        raise AssertionError("No continuar con dictamen después de una decisión inválida")

    with pytest.raises(LLMError) as error:
        ejecutar_agente(entrada(), planificador=planner, analizador=analizador_prohibido)
    assert error.value.codigo == 502
    assert decisiones == [1]


def test_planificador_503_no_filtra_error_crudo(monkeypatch):
    from unittest.mock import Mock
    from google import genai
    from google.genai import errors
    import app.services.agente as agente_modulo
    from app.services.llm import LLMError

    monkeypatch.setenv("GEMINI_API_KEY", "clave-sintetica")
    cliente = Mock()
    secreto = "MARCADOR_INTERNO_QUE_NO_SE_PUBLICA"
    cliente.models.generate_content.side_effect = errors.APIError(
        503, {"message": secreto}
    )
    monkeypatch.setattr(genai, "Client", Mock(return_value=cliente))

    with pytest.raises(LLMError) as error:
        agente_modulo.planificar_gemini("print('hola')", [])
    assert error.value.codigo == 503
    assert secreto not in str(error.value)
    cliente.close.assert_called_once()


def test_planificador_504_informa_timeout_seguro(monkeypatch):
    from unittest.mock import Mock
    from google import genai
    from google.genai import errors
    import app.services.agente as agente_modulo
    from app.services.llm import LLMError

    monkeypatch.setenv("GEMINI_API_KEY", "clave-sintetica")
    cliente = Mock()
    cliente.models.generate_content.side_effect = errors.APIError(
        504, {"message": "detalle interno"}
    )
    monkeypatch.setattr(genai, "Client", Mock(return_value=cliente))

    with pytest.raises(LLMError) as error:
        agente_modulo.planificar_gemini("print('hola')", [])
    assert error.value.codigo == 504
    assert "detalle interno" not in str(error.value)
    cliente.close.assert_called_once()


def test_planificador_respuesta_json_invalida_es_502(monkeypatch):
    from unittest.mock import Mock
    from google import genai
    import app.services.agente as agente_modulo
    from app.services.llm import LLMError

    monkeypatch.setenv("GEMINI_API_KEY", "clave-sintetica")
    cliente = Mock()
    cliente.models.generate_content.return_value.text = '{"herramienta":"borrar_archivos","motivo":"malicioso"}'
    monkeypatch.setattr(genai, "Client", Mock(return_value=cliente))

    with pytest.raises(LLMError) as error:
        agente_modulo.planificar_gemini("print('hola')", [])
    assert error.value.codigo == 502
    cliente.close.assert_called_once()


def test_dashboard_explicita_modo_degradado():
    r = client.get("/agente/demo")
    assert r.status_code == 200
    assert "ANÁLISIS PARCIAL" in r.text
    assert "ANÁLISIS PARCIAL:" in r.text
    assert "report.mensaje" in r.text
    assert "No hay dictamen de IA ni citas RAG" in r.text


def test_previsualizacion_ast_protegida_por_limite_de_tasa():
    # La ruta local también consume CPU y debe quedar protegida en Railway.
    from app.services.rate_limit import ENDPOINT_WEIGHTS
    assert ENDPOINT_WEIGHTS["/api/v1/agente/previsualizar"] == 1
    assert ENDPOINT_WEIGHTS["/api/v1/agente/analizar"] == 3


def test_decisiones_gemini_quedan_registradas_en_exito():
    secuencia = iter([
        DecisionAgente(herramienta="detectar_llamadas_sensibles", motivo="Revisar eval"),
        DecisionAgente(herramienta="finalizar", motivo="Evidencia suficiente"),
    ])
    resultado = ejecutar_agente(
        entrada(),
        planificador=lambda codigo, pasos: next(secuencia),
        analizador=informe_ficticio,
    )
    pasos, informe = resultado
    assert informe.hallazgos == []
    assert [p.origen for p in pasos] == ["automatico", "gemini"]
    assert [d.herramienta for d in resultado.decisiones] == [
        "detectar_llamadas_sensibles", "finalizar"
    ]
    assert [d.estado for d in resultado.decisiones] == ["ejecutada", "finalizar"]
    assert resultado.decisiones[0].motivo == "Revisar eval"


def test_informe_503_conserva_decisiones_e_inspeccion_gemini(monkeypatch):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    decisiones = iter([
        DecisionAgente(herramienta="detectar_llamadas_sensibles", motivo="Investigar eval"),
        DecisionAgente(herramienta="finalizar", motivo="Sin otros análisis"),
    ])

    def fallar_informe(codigo):
        raise LLMError("ERROR_INTERNO_PRIVADO_NO_PUBLICAR", 503)

    def ejecutar_con_fallo(solicitud):
        return ejecutar_agente(
            solicitud,
            planificador=lambda codigo, pasos: next(decisiones),
            analizador=fallar_informe,
        )

    monkeypatch.setattr(route_module, "ejecutar_agente", ejecutar_con_fallo)
    respuesta = client.post("/api/v1/agente/analizar", json=entrada().model_dump())
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["modo"] == "degradado"
    assert datos["fase_error"] == "informe"
    assert datos["informe"]["estado"] == "parcial"
    assert datos["informe"]["hallazgos"] == []
    assert datos["informe"]["fuentes"] == []
    assert [d["herramienta"] for d in datos["decisiones"]] == [
        "detectar_llamadas_sensibles", "finalizar"
    ]
    assert [p["origen"] for p in datos["pasos"]] == [
        "automatico", "gemini", "local"
    ]
    assert len(set(p["herramienta"] for p in datos["pasos"])) == 3
    assert len(datos["pasos"]) == datos["max_pasos"] == 3
    assert "ERROR_INTERNO_PRIVADO_NO_PUBLICAR" not in respuesta.text


def test_planificador_503_conserva_sus_pasos_anteriores(monkeypatch):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    def elegir(codigo, pasos):
        if len(pasos) == 1:
            return DecisionAgente(
                herramienta="revisar_consultas_sql", motivo="Inspección SQL"
            )
        raise LLMError("MARCADOR_PRIVADO_503", 503)

    def ejecutar_con_fallo(solicitud):
        return ejecutar_agente(
            solicitud, planificador=elegir, analizador=informe_ficticio
        )

    monkeypatch.setattr(route_module, "ejecutar_agente", ejecutar_con_fallo)
    respuesta = client.post("/api/v1/agente/analizar", json=entrada().model_dump())
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["fase_error"] == "planificacion"
    assert datos["modo"] == "degradado"
    assert [p["herramienta"] for p in datos["pasos"]] == [
        "inspeccionar_estructura", "revisar_consultas_sql", "detectar_llamadas_sensibles"
    ]
    assert [p["origen"] for p in datos["pasos"]] == [
        "automatico", "gemini", "local"
    ]
    assert len(datos["decisiones"]) == 1
    assert datos["decisiones"][0]["herramienta"] == "revisar_consultas_sql"
    assert "MARCADOR_PRIVADO_503" not in respuesta.text


def test_maximo_un_paso_no_finge_planificacion_gemini(monkeypatch):
    import app.routes.agente as route_module
    from app.services.llm import LLMError

    def no_planificar(*args):
        raise AssertionError("No debe consultarse planificador con max_pasos=1")

    def fallar_informe(codigo):
        raise LLMError("Proveedor temporalmente no disponible", 503)

    monkeypatch.setattr(
        route_module, "ejecutar_agente",
        lambda solicitud: ejecutar_agente(
            solicitud, planificador=no_planificar, analizador=fallar_informe
        ),
    )
    respuesta = client.post(
        "/api/v1/agente/analizar", json=entrada(pasos=1).model_dump()
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["modo"] == "degradado"
    assert datos["fase_error"] == "informe"
    assert datos["decisiones"] == []
    assert len(datos["pasos"]) == 1
    assert datos["pasos"][0]["origen"] == "automatico"


def test_ejecucion_agente_conserva_validacion_byte_nulo():
    with pytest.raises(ValueError):
        ejecutar_agente(
            entrada(codigo="print(1)\x00"),
            planificador=lambda *args: DecisionAgente(
                herramienta="finalizar", motivo="Sin inspección"
            ),
            analizador=informe_ficticio,
        )


def test_panel_muestra_origen_y_decisiones_verificables():
    respuesta = client.get("/agente/demo")
    assert respuesta.status_code == 200
    assert "Decisiones registradas del planificador" in respuesta.text
    assert "ELEGIDO POR GEMINI" in respuesta.text
    assert "RESPALDO LOCAL" in respuesta.text
