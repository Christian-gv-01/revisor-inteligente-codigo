"""Ejemplos de contrato reproducibles: proveedor, RAG y estático siempre simulados."""
from pathlib import Path
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
CODIGO = "usuario = input()\nconsulta = 'SELECT ' + usuario\ncursor.execute(consulta)\n"
FUENTE = {"id":"seguridad_python-002", "texto":"Usar consultas parametrizadas para separar datos de SQL.",
    "coleccion":"seguridad_python", "tipo_fuente":"seguridad", "area":"seguridad",
    "documento":"seguridad_python.md", "seccion":"Regla 2", "fuente":"OWASP",
    "url":"https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html", "distancia":0.1}


def generar(destino: Path) -> dict:
    with patch.dict(os.environ, {"GEMINI_API_KEY":"fixture-local", "RATE_LIMIT_ENABLED":"0",
        "CONCURRENCY_LIMIT_ENABLED":"0", "STATIC_ANALYSIS_ENABLED":"0"}):
        from fastapi.testclient import TestClient
        import app.main as api
        from app.services import agente, llm, rag, correcciones
        from app.services.static_analysis import ResultadoEstatico

        ampliar = {"herramienta":"ampliar_contexto", "motivo":"Comprobar la construcción SQL y su uso cercano.", "argumentos":{"linea":2}}
        buscar = {"herramienta":"buscar_referencia", "motivo":"Recuperar respaldo documental para SQL.", "argumentos":{"categoria":"inyeccion_sql"}}
        finalizar = {"herramienta":"finalizar", "motivo":"La evidencia reunida permite pasar a la síntesis.", "argumentos":{}}
        solicitud = {"archivo":"ejemplo.py", "codigo":CODIGO, "max_pasos":3, "version_herramientas":"2"}
        temprana = {**solicitud, "codigo":"print('hola')\n"}
        class ClienteFixture:
            def __init__(self, **kw): self.models = self
            def close(self): pass
            def generate_content(self, **kw):
                hallazgos = []
                if "SELECT" in kw["contents"]:
                    hallazgos = [{"linea":2, "severidad":"alta", "categoria":"Inyección SQL",
                        "titulo":"Consulta dinámica de ejemplo", "explicacion":"Salida sintética para revisar el contrato.",
                        "correccion_sugerida":"Separar datos y consulta mediante parámetros.",
                        "referencias":[FUENTE["id"]], "fragmento_codigo":"consulta = 'SELECT ' + usuario"}]
                return SimpleNamespace(text=json.dumps({"hallazgos":hallazgos}), usage_metadata=None)

        def ejecutar(payload, decisiones, fallo=False):
            pendientes = iter(decisiones)
            def elegir(c, p, **kw): return next(pendientes)
            def estatico(c, archivo):
                return ResultadoEstatico(archivo=archivo, estado="completo", hallazgos=[], herramientas=[
                    {"herramienta": "ruff", "estado": "ok", "hallazgos": 0},
                    {"herramienta": "bandit", "estado": "ok", "hallazgos": 0},
                ])
            with patch.object(correcciones, "limpiar_caducadas", lambda: None), \
                patch.object(agente, "planificar_gemini", elegir), \
                patch.object(agente, "analizar_estatico", estatico), \
                patch.object(llm.genai, "Client", ClienteFixture), \
                patch.object(llm, "_recuperar_contexto_rag", lambda c: ("Referencia sintética", [FUENTE])), \
                patch.object(rag, "buscar_fragmentos", side_effect=RuntimeError("DETALLE_PRIVADO_INTERNO") if fallo else None,
                    return_value=[FUENTE]), TestClient(api.app) as cliente:
                respuesta = cliente.post("/api/v1/agente/analizar", json=payload)
                assert respuesta.status_code == 200
                datos = respuesta.json()
                assert "DETALLE_PRIVADO_INTERNO" not in respuesta.text
                return datos

        ejemplos = {
            "01-solicitud-contexto-y-referencia.json":solicitud,
            "02-decision-ampliar-contexto.json":ampliar,
            "03-decision-buscar-referencia.json":buscar,
            "04-respuesta-contexto-y-referencia.json":ejecutar(solicitud, [ampliar, buscar]),
            "05-solicitud-finalizacion-anticipada.json":temprana,
            "06-decision-finalizar.json":finalizar,
            "07-respuesta-finalizacion-anticipada.json":ejecutar(temprana, [finalizar]),
            "08-respuesta-error-herramienta.json":ejecutar(solicitud, [buscar], fallo=True),
            "09-respuesta-v1-compatible.json":ejecutar({k:v for k,v in solicitud.items() if k!="version_herramientas"}, [finalizar]),
            "10-esquema-decision.json":agente.DecisionAgente.model_json_schema(),
        }
        destino.mkdir(parents=True, exist_ok=True)
        for nombre, valor in ejemplos.items():
            (destino/nombre).write_text(json.dumps(valor, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        return ejemplos


if __name__ == "__main__":
    generar(Path(__file__).resolve().parent)
    print("Diez ejemplos sintéticos generados, sin red ni consumo de Gemini.")
