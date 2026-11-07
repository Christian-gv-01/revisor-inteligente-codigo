"""Contrato sintético API → frontend: analizadores/proveedor sustituidos, sin IA externa."""
from pathlib import Path
import json
import os
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
CODIGO = "import os\neval(input())\n"


def generar():
    from fastapi.testclient import TestClient
    import app.main as api
    from app.services import static_analysis as estatico, correcciones
    from app.services.llm import LLMError

    base = {"test_name": "fixture_prioridad", "issue_text": "Indicador sintético de orden; no diagnóstico real.",
            "line_number": 2, "issue_severity": "HIGH", "more_info": "https://bandit.readthedocs.io/"}
    bandit = [
        {**base, "test_id": "B001", "issue_confidence": None},
        {**base, "test_id": "B002", "issue_confidence": "LOW"},
        {**base, "test_id": "B003", "issue_confidence": "HIGH"},
        {**base, "test_id": "B004", "issue_confidence": "HIGH", "line_number": 1},
        {**base, "test_id": "B005", "issue_confidence": "MEDIUM"},
        {**base, "test_id": "B006", "issue_severity": "MEDIUM", "issue_confidence": "HIGH"},
    ]
    ruff = [{"code": "F401", "message": "Importación sintética sin uso", "location": {"row": 1, "column": 1}}]
    def ejecutar(comando, **_):
        return "ok", json.dumps(ruff if "ruff" in comando else {"results": bandit})
    with patch.dict(os.environ, {"STATIC_ANALYSIS_ENABLED": "1", "RATE_LIMIT_ENABLED": "0",
            "CONCURRENCY_LIMIT_ENABLED": "0", "PROJECT_BUDGET_ENABLED": "0"}), \
         patch.object(estatico, "_ejecutar", ejecutar), \
         patch.object(api, "analizar_codigo", side_effect=LLMError("Proveedor simulado no disponible", 503)), \
         patch.object(correcciones, "limpiar_caducadas", lambda: None), TestClient(api.app) as cliente:
        respuesta = cliente.post("/api/v1/analizar", json={"archivo": "prioridad.py", "codigo": CODIGO})
        assert respuesta.status_code == 200
        datos = respuesta.json()
    assert datos["estado"] == "parcial"
    assert [h["regla"] for h in datos["analisis_estatico"]["hallazgos"]] == ["B003", "B004", "B005", "B002", "B001", "B006", "F401"]
    return {"tipo": "fixture_sintetico", "ia_externa": False, "analizadores": "salidas simuladas",
            "api": "FastAPI y normalización reales", "codigo": CODIGO, "respuesta": datos}


if __name__ == "__main__":
    destino = ROOT / "frontend/tests/fixtures/prioridad-integrada.json"
    destino.write_text(json.dumps(generar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Fixture de contrato regenerado; no son resultados de Gemini ni de analizadores reales.")
