"""Regresiones del informe real y sus adaptadores, sin proveedor externo."""
import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
import httpx
from fastapi.testclient import TestClient

import app.main as api
import app.routes.agente as rutas_agente
from app.models.analisis import InformeModelo
from app.services import llm
from app.services.agente import SolicitudAgente, inspeccion_local
from app.services.evidencia import EvidenciaRevision
from app.services.static_analysis import ResultadoEstatico

CODIGO = "consulta = 'SELECT * FROM usuarios'"
FUENTE = {"id": "seguridad_python-002", "documento": "seguridad_python.md"}


def hallazgo(referencias):
    return {
        "linea": 1, "severidad": "alta", "categoria": "Inyeccion SQL",
        "titulo": "Consulta concatenada", "explicacion": "Revisar datos de entrada.",
        "correccion_sugerida": "Parametrizar.", "referencias": referencias,
        "fragmento_codigo": CODIGO,
    }


@pytest.fixture
def proveedor(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fixture-local")
    monkeypatch.setenv("STATIC_ANALYSIS_ENABLED", "0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("CONCURRENCY_LIMIT_ENABLED", "0")
    recuperar = lambda *args: ("Documento recuperado", [FUENTE.copy()])
    monkeypatch.setattr(llm, "_recuperar_contexto_rag", recuperar)
    monkeypatch.setattr(llm, "_recuperar_contexto_agente", recuperar)
    cliente = Mock()
    cliente.models.generate_content.return_value.usage_metadata = None
    monkeypatch.setattr(llm.genai, "Client", Mock(return_value=cliente))
    return cliente


def respuesta(proveedor, datos):
    proveedor.models.generate_content.return_value.text = json.dumps(datos)


def analizar(con_agente=False):
    if con_agente:
        evidencia = EvidenciaRevision(archivo="ejemplo.py", inspecciones=[],
            estado_estatico="completo", total_reglas=0, reglas=[])
        return llm.analizar_codigo(CODIGO, evidencia=evidencia)
    return llm.analizar_codigo(CODIGO)


@pytest.mark.parametrize("con_agente", [False, True])
@pytest.mark.parametrize("mensaje", ["No hay evidencia suficiente.", None, "   "])
def test_conserva_abstencion_explicita(proveedor, con_agente, mensaje):
    respuesta(proveedor, {"estado": "abstenido", "mensaje": mensaje, "hallazgos": []})
    informe = analizar(con_agente)
    assert informe.estado_validado == "abstenido"
    assert informe.mensaje_validado and informe.mensaje_validado.strip()
    if mensaje and mensaje.strip():
        assert informe.mensaje_validado == mensaje
    assert informe.hallazgos == []
    assert informe.fuentes == [FUENTE]
    proveedor.close.assert_called_once()


@pytest.mark.parametrize("con_agente", [False, True])
def test_abstencion_no_publica_hallazgos_contradictorios(proveedor, con_agente):
    respuesta(proveedor, {"estado": "abstenido", "mensaje": "No puedo concluir.",
        "hallazgos": [hallazgo([FUENTE["id"]])]})
    informe = analizar(con_agente)
    assert informe.estado_validado == "abstenido"
    assert informe.hallazgos == []


@pytest.mark.parametrize("refs", [[], ["inventada"], [FUENTE["id"], "inventada"]])
@pytest.mark.parametrize("con_agente", [False, True])
def test_conserva_validos_con_revision_parcial(proveedor, refs, con_agente):
    respuesta(proveedor, {"hallazgos": [hallazgo(refs), hallazgo([" " + FUENTE["id"] + " ", FUENTE["id"]])]})
    informe = analizar(con_agente)
    assert informe.estado_validado == "parcial"
    assert len(informe.hallazgos) == 1
    assert informe.hallazgos[0].referencias == [FUENTE["id"]]
    assert "1 hallazgo" in informe.mensaje_validado
    assert informe.fuentes == [FUENTE]


@pytest.mark.parametrize("con_agente", [False, True])
def test_lista_vacia_analizada_no_es_abstencion(proveedor, con_agente):
    respuesta(proveedor, {"estado": "analizado", "hallazgos": []})
    informe = analizar(con_agente)
    assert informe.estado_validado == "analizado"
    assert informe.mensaje_validado is None


def enviar(cliente, modalidad, archivos=2):
    if modalidad == "codigo":
        return cliente.post("/api/v1/analizar", json={"archivo": "ejemplo.py", "codigo": CODIGO})
    if modalidad == "python":
        return cliente.post("/api/v1/archivos", files={"archivo": ("ejemplo.py", CODIGO.encode())})
    if modalidad == "github":
        return cliente.post("/api/v1/repositorios/github", json={"url": "https://github.com/grupo/proyecto"})
    if modalidad == "agente":
        return cliente.post("/api/v1/agente/analizar", json={"archivo": "ejemplo.py", "codigo": CODIGO})
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archivo:
        for nombre in ("uno.py", "dos.py", "tres.py")[:archivos]:
            archivo.writestr(nombre, CODIGO)
    return cliente.post("/api/v1/archivos/zip", files={"archivo": ("ejemplos.zip", buffer.getvalue())})


@pytest.mark.parametrize("modalidad", ["codigo", "python", "zip", "github", "agente"])
@pytest.mark.parametrize("estado", ["abstenido", "parcial"])
def test_estado_y_mensaje_llegan_a_http(proveedor, monkeypatch, modalidad, estado):
    if estado == "abstenido":
        datos = {"estado": estado, "mensaje": "Evidencia insuficiente.", "hallazgos": []}
    else:
        datos = {"hallazgos": [hallazgo([FUENTE["id"]]), hallazgo(["inventada"])]}
    respuesta(proveedor, datos)
    monkeypatch.setattr(api, "obtener_archivos_python_github", lambda url: [("uno.py", CODIGO), ("dos.py", CODIGO)])
    # El planificador se sustituye; la síntesis y la validación LLM son reales.
    def ejecutar(solicitud):
        return inspeccion_local(SolicitudAgente(archivo="ejemplo.py", codigo=CODIGO)), analizar(True)
    monkeypatch.setattr(rutas_agente, "ejecutar_agente", ejecutar)
    with TestClient(api.app) as cliente:
        r = enviar(cliente, modalidad)
    assert r.status_code == 200, r.text
    datos_http = r.json()
    informes = datos_http["informes"] if modalidad in ("zip", "github") else [datos_http["informe"] if modalidad == "agente" else datos_http]
    for informe in informes:
        assert informe["estado"] == estado
        assert informe["mensaje"]
        assert len(informe["hallazgos"]) == (1 if estado == "parcial" else 0)
        assert informe["fuentes"][0]["id"] == FUENTE["id"]
    if modalidad in ("zip", "github"):
        assert proveedor.models.generate_content.call_count == 2
        if estado == "parcial":
            assert datos_http["estado"] == "parcial"


def test_adaptador_http_respeta_estado_explicito_sin_metadatos():
    informe = InformeModelo(estado="abstenido", mensaje="No concluyente.", hallazgos=[])
    salida = api.construir_respuesta("ejemplo.py", informe)
    assert salida.estado == "abstenido"
    assert salida.mensaje == "No concluyente."


def test_ruta_directa_no_exige_el_fragmento_del_contrato_agente(proveedor):
    valido = hallazgo([FUENTE["id"]])
    del valido["fragmento_codigo"]
    respuesta(proveedor, {"hallazgos": [valido, hallazgo(["inventada"])]})
    informe = analizar()
    assert informe.estado_validado == "parcial"
    assert len(informe.hallazgos) == 1
    assert informe.hallazgos[0].fragmento_codigo is None


@pytest.mark.parametrize("modalidad", ["zip", "github"])
def test_parcial_documental_seguido_de_caida_conserva_respaldo(proveedor, monkeypatch, modalidad):
    """Una omisión de cita no activa el cortacircuito; un timeout posterior sí."""
    nombres = ("uno.py", "dos.py", "tres.py")
    monkeypatch.setattr(api, "obtener_archivos_python_github", lambda url: [(n, CODIGO) for n in nombres])
    async def estatico(codigo, archivo):
        return ResultadoEstatico(archivo=archivo, estado="completo", hallazgos=[], herramientas=[])
    monkeypatch.setattr(api, "_analisis_estatico_si_habilitado", estatico)
    proveedor.models.generate_content.side_effect = [
        SimpleNamespace(text=json.dumps({"hallazgos": [hallazgo([FUENTE["id"]]), hallazgo(["inventada"])]}), usage_metadata=None),
        httpx.TimeoutException("Timeout controlado"),
    ]
    with TestClient(api.app) as cliente:
        r = enviar(cliente, modalidad, archivos=3)
    assert r.status_code == 200, r.text
    datos = r.json()
    assert datos["estado"] == "parcial"
    primero, segundo, tercero = datos["informes"]
    assert all(i["estado"] == "parcial" for i in datos["informes"])
    assert len(primero["hallazgos"]) == 1 and primero["fuentes"]
    for informe in (segundo, tercero):
        assert informe["hallazgos"] == [] and informe["fuentes"] == []
        assert informe["analisis_estatico"]["estado"] == "completo"
    assert proveedor.models.generate_content.call_count == 2
