"""Contrato de herencia generado por FastAPI; SDK, RAG y estático simulados."""
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def generar():
    from fastapi.testclient import TestClient
    import app.main as api
    from app.services import agente, correcciones, llm
    from app.services.static_analysis import HallazgoEstatico, ResultadoEstatico

    entrada = {"archivo": "muestra.py", "codigo": "import subprocess\nsubprocess.run(input(), shell=True)\n"}
    fuente = {"id": "seguridad_python-fixture", "texto": "Referencia sintética para revisar el contrato.",
        "area": "seguridad", "documento": "fixture", "seccion": "fixture", "fuente": "fixture",
        "url": "https://cwe.mitre.org/data/definitions/78.html", "distancia": 0.1}

    class SDK:
        def __init__(self, **kw): self.models = self
        def close(self): pass
        def generate_content(self, *, contents, **kw):
            if contents.startswith("DATOS_PLANIFICACION_NO_CONFIABLES_JSON:"):
                datos = {"herramienta": "finalizar", "argumentos": {}, "motivo": "Evidencia suficiente para el fixture"}
            else:
                evidencia = json.loads(contents.split("DATOS_NO_CONFIABLES_JSON:\n", 1)[1])["evidencia_herramientas_no_confiable"]
                datos = {"hallazgos": [{"linea": 2, "severidad": "baja", "categoria": "Inyección comandos",
                    "titulo": "Hallazgo sintético", "explicacion": "Prueba de trazabilidad, no evaluación real",
                    "correccion_sugerida": "Revisar", "referencias": [fuente["id"]],
                    "fragmento_codigo": "subprocess.run(input(), shell=True)",
                    "reglas_evidencia": [evidencia["reglas"][0]["id"]]}]}
            return SimpleNamespace(text=json.dumps(datos), usage_metadata=None)

    def estatico(codigo, archivo):
        return ResultadoEstatico(archivo=archivo, estado="completo", herramientas=[
            {"herramienta": "ruff", "estado": "ok", "hallazgos": 0},
            {"herramienta": "bandit", "estado": "ok", "hallazgos": 1}], hallazgos=[
            HallazgoEstatico(herramienta="bandit", regla="B602", tipo="seguridad", linea=2, columna=1,
                severidad="alta", confianza="alta", titulo="Fixture estático", descripcion="Simulado")])

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fixture-local", "RATE_LIMIT_ENABLED": "0",
        "CONCURRENCY_LIMIT_ENABLED": "0", "ANONYMIZED_TELEMETRY": "False", "OTEL_SDK_DISABLED": "true"}), \
        patch.object(agente, "analizar_estatico", estatico), patch.object(llm.genai, "Client", SDK), \
        patch.object(llm, "_recuperar_contexto_rag", lambda c: ("Contexto simulado", [fuente])), \
        patch.object(llm, "_recuperar_contexto_agente", lambda c, e: ("Contexto simulado", [fuente])), \
        patch.object(correcciones, "limpiar_caducadas", lambda: None), TestClient(api.app) as cliente:
        r = cliente.post("/api/v1/agente/analizar", json={**entrada, "version_herramientas": "2", "max_pasos": 4})
        assert r.status_code == 200
        return {"proveedores": "todos simulados", "entrada": entrada, "respuesta": r.json()}


if __name__ == "__main__":
    archivo = ROOT / "frontend/tests/fixtures/herencia-integrada.json"
    archivo.write_text(json.dumps(generar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
