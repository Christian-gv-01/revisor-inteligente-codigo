import importlib.util
import json
from pathlib import Path


def test_json_frontend_se_regenera_desde_fastapi_y_hereda_sin_ventana():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("fixture_herencia", root / "qa/fixture_herencia_integrada.py")
    modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
    datos = modulo.generar()
    assert datos == json.loads((root / "frontend/tests/fixtures/herencia-integrada.json").read_text(encoding="utf-8"))
    h = datos["respuesta"]["informe"]["hallazgos"][0]
    assert h["severidad"] == "critica" and h["severidad_original_modelo"] == "baja"
    assert h["herencia_severidad"][0]["severidad_original"] == "alta"
    assert len(datos["respuesta"]["pasos"]) == 1
