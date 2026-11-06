"""Los ejemplos publicados deben coincidir con respuestas reales del backend fixture."""
import importlib.util
import json
from pathlib import Path

from app.services.agente import SolicitudAgente, RespuestaAgente, DecisionAgente

CARPETA = Path(__file__).resolve().parents[2] / "docs/contrato-agente-v2"


def test_ejemplos_se_regeneran_y_validan_con_modelos_actuales(tmp_path):
    spec = importlib.util.spec_from_file_location("contrato_fixture", CARPETA/"generar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    ejemplos = modulo.generar(tmp_path)
    assert len(ejemplos) == 10
    for nombre, datos in ejemplos.items():
        assert json.loads((CARPETA/nombre).read_text(encoding="utf-8")) == datos
        if "solicitud" in nombre: SolicitudAgente.model_validate(datos)
        if "decision-" in nombre: DecisionAgente.model_validate(datos)
        if "respuesta" in nombre: RespuestaAgente.model_validate(datos)
    normal = ejemplos["04-respuesta-contexto-y-referencia.json"]
    assert normal["terminacion"] == "max_pasos" and len(normal["pasos"]) == 3
    assert ejemplos["07-respuesta-finalizacion-anticipada.json"]["terminacion"] == "finalizacion_anticipada"
    assert ejemplos["08-respuesta-error-herramienta.json"]["fase_error"] == "herramienta"
    assert "version_herramientas" not in ejemplos["09-respuesta-v1-compatible.json"]
