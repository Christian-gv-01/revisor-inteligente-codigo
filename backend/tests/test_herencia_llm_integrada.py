"""Recorrido evidencia → SDK simulado → validación → herencia → respuesta."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services import llm
from app.services.evidencia import construir_evidencia
from app.services.static_analysis import HallazgoEstatico, ResultadoEstatico

CODIGO = "import subprocess\nsubprocess.run(input(), shell=True)\n"
FUENTE = {"id": "seguridad_python-003", "texto": "Referencia sintética sobre comandos.",
    "area": "seguridad", "documento": "fixture", "seccion": "fixture", "fuente": "fixture",
    "url": "https://cwe.mitre.org/data/definitions/78.html", "distancia": 0.1}


def preparar(monkeypatch, *, seleccion="valida", auditoria_falsa=False, malformada=False):
    monkeypatch.setenv("GEMINI_API_KEY", "fixture-local")
    monkeypatch.setattr(llm, "_recuperar_contexto_rag", lambda c: ("Contexto sintético", [FUENTE]))
    monkeypatch.setattr(llm, "_recuperar_contexto_agente", lambda c, e: ("Contexto sintético", [FUENTE]))
    e = construir_evidencia("muestra.py", [], ResultadoEstatico(archivo="muestra.py", estado="completo",
        herramientas=[], hallazgos=[HallazgoEstatico(herramienta="bandit", regla="B602", tipo="seguridad",
            linea=2, severidad="alta", confianza="alta", titulo="Fixture", descripcion="Fixture")]))
    ids = [e.reglas[0].id] if seleccion == "valida" else ["estatica-" + "a" * 64] if seleccion == "desconocida" else []
    h = {"linea": 2, "severidad": "baja", "categoria": "Inyección comandos", "titulo": "Fixture",
        "explicacion": "Salida simulada", "correccion_sugerida": "Revisar", "referencias": [FUENTE["id"]],
        "fragmento_codigo": "subprocess.run(input(), shell=True)", "reglas_evidencia": ids}
    if auditoria_falsa:
        h.update(severidad_original_modelo="alta", herencia_severidad=[{
            "id": "fabricado", "herramienta": "bandit", "regla": "B602", "linea": 2,
            "severidad_original": "alta", "severidad_derivada": "critica"}])
    if malformada:
        h.update(severidad_original_modelo=123, herencia_severidad="auditoría no autorizada")
    sdk = Mock()
    sdk.models.generate_content.return_value = SimpleNamespace(text=json.dumps({"hallazgos": [h]}), usage_metadata=None)
    monkeypatch.setattr(llm.genai, "Client", Mock(return_value=sdk))
    return e, sdk


def test_hereda_sin_ventana_solo_id_ofrecido_y_conserva_auditoria(monkeypatch):
    e, sdk = preparar(monkeypatch)
    informe = llm.analizar_codigo(CODIGO, evidencia=e)
    h = informe.hallazgos[0]
    assert informe.estado_validado == "analizado" and h.severidad == "critica"
    assert h.severidad_original_modelo == "baja" and h.herencia_severidad[0].id == e.reglas[0].id
    schema = sdk.models.generate_content.call_args.kwargs["config"].response_schema.model_json_schema()
    props = schema["$defs"]["HallazgoGenerativo"]["properties"]
    assert "herencia_severidad" not in props


def test_vinculo_desconocido_no_descarta_hallazgo_valido_y_marca_parcial(monkeypatch):
    e, _ = preparar(monkeypatch, seleccion="desconocida")
    informe = llm.analizar_codigo(CODIGO, evidencia=e)
    assert informe.estado_validado == "parcial" and len(informe.hallazgos) == 1
    h = informe.hallazgos[0]
    assert h.severidad == "baja" and not h.reglas_evidencia and not h.herencia_severidad


@pytest.mark.parametrize("agente", [False, True])
def test_modelo_no_puede_fabricar_auditoria_en_ninguna_ruta(monkeypatch, agente):
    e, _ = preparar(monkeypatch, seleccion="sin_cita", auditoria_falsa=True)
    informe = llm.analizar_codigo(CODIGO, **({"evidencia": e} if agente else {}))
    h = informe.hallazgos[0]
    assert h.severidad == "baja" and h.severidad_original_modelo is None and not h.herencia_severidad


@pytest.mark.parametrize("agente", [False, True])
def test_auditoria_fuera_de_esquema_no_elimina_el_hallazgo_valido(monkeypatch, agente):
    e, _ = preparar(monkeypatch, seleccion="sin_cita", malformada=True)
    informe = llm.analizar_codigo(CODIGO, **({"evidencia": e} if agente else {}))
    assert len(informe.hallazgos) == 1 and informe.hallazgos[0].severidad == "baja"
