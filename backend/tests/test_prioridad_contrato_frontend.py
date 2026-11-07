"""El fixture consumido por frontend corresponde a la salida actual de la API."""
from pathlib import Path
import json
import runpy


def test_api_prioridad_conserva_contrato_consumido_por_frontend():
    root = Path(__file__).resolve().parents[2]
    generado = runpy.run_path(str(root / "qa/fixture_prioridad_integrada.py"))["generar"]()
    publicado = json.loads((root / "frontend/tests/fixtures/prioridad-integrada.json").read_text(encoding="utf-8"))
    assert generado == publicado
    hallazgos = generado["respuesta"]["analisis_estatico"]["hallazgos"]
    assert [h["confianza"] for h in hallazgos] == ["alta", "alta", "media", "baja", None, "alta", None]
    assert [h["severidad"] for h in hallazgos] == ["alta"] * 5 + ["media", "baja"]
