"""Candidato v2 real en loopback; sustituye exclusivamente el SDK de IA."""
from contextlib import ExitStack
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "eval"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    folder = args.output.resolve()
    if folder.exists():
        parser.error("La carpeta de evidencia debe ser nueva.")
    folder.mkdir(parents=True)
    from run_integration import FixtureClient
    from run_eval import prepare_rag
    import uvicorn

    class Client(FixtureClient):
        plans = 0
        syntheses = 0
        propagation = []

        def generate_content(self, *, contents, **kw):
            marker = "DATOS_PLANIFICACION_NO_CONFIABLES_JSON:\n"
            if contents.startswith(marker):
                Client.plans += 1
                data = json.loads(contents[len(marker):])
                code = data["codigo_no_confiable"]
                previous = data["resultados_previos_no_confiables"]
                if "V2_EARLY" in code:
                    tool, arguments = "finalizar", {}
                elif "V2_ERROR" in code:
                    tool, arguments = "ampliar_contexto", {"linea": 999}
                elif len(previous) == 1 or "V2_REPEAT" in code:
                    tool, arguments = "ampliar_contexto", {"linea": 2}
                elif "V2_FOUR" in code and len(previous) == 3:
                    tool, arguments = "ampliar_contexto", {"linea": 1}
                else:
                    assert previous[1]["resultado"]["linea_objetivo"] == 2
                    Client.propagation.append("contexto_en_siguiente_decision")
                    tool, arguments = "buscar_referencia", {"categoria": "inyeccion_sql"}
                return SimpleNamespace(text=json.dumps({"herramienta": tool, "argumentos": arguments,
                    "motivo": "Acción controlada del proveedor simulado para probar el contrato visual."}),
                    usage_metadata=SimpleNamespace(prompt_token_count=10, candidates_token_count=2, total_token_count=12))
            payload = json.loads(contents.split("DATOS_NO_CONFIABLES_JSON:\n", 1)[1])
            code = payload["codigo_python_no_confiable"]
            evidence = payload["evidencia_herramientas_no_confiable"]
            Client.syntheses += 1
            if "V2_FULL" in code or "V2_FOUR" in code:
                assert evidence["contextos_ampliados"][0]["linea_objetivo"] == 2
                assert evidence["referencias_buscadas"][0]["fragmentos"]
                Client.propagation.append("contexto_y_referencias_en_sintesis")
                if "V2_FOUR" in code:
                    assert len(evidence["contextos_ampliados"]) == 2
                    Client.propagation.append("cuarto_paso_en_sintesis")
            result = super().generate_content(contents=contents, **kw)
            result.usage_metadata = SimpleNamespace(prompt_token_count=10, candidates_token_count=2, total_token_count=12)
            return result

    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {
            "PROJECT_BUDGET_ENABLED": "0", "CORRECTIONS_COOKIE_SECURE": "0",
            "RATE_LIMIT_ENABLED": "0", "CONCURRENCY_LIMIT_ENABLED": "0",
            "STATIC_ANALYSIS_ENABLED": "1", "GEMINI_API_KEY": "fixture-sin-credencial-real",
            "GEMINI_MODEL": "fixture-integracion", "LLM_RETRY_ATTEMPTS": "2",
        }))
        from app.main import app
        from app.services import correcciones, llm
        stack.enter_context(patch.object(correcciones, "DB_PATH", folder / "correcciones.sqlite3"))
        stack.enter_context(patch.object(llm.genai, "Client", Client))
        prepare_rag()

        @app.get("/__agent_v2_fixture__/status")
        async def status():
            return {"proveedor": "simulado", "planes": Client.plans, "sintesis": Client.syntheses,
                    "propagacion": Client.propagation}

        sock = stack.enter_context(socket.socket())
        sock.bind(("127.0.0.1", 0))
        sock.listen(128)
        server = uvicorn.Server(uvicorn.Config(app, log_level="warning", access_log=False))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        def stop():
            server.should_exit = True
            thread.join(timeout=5)
        stack.callback(stop)
        deadline = time.monotonic() + 15
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(.05)
        if not server.started:
            raise RuntimeError("No inició la API fixture.")
        env = {**os.environ, "CODEGUARD_DEV_API_TARGET": f"http://127.0.0.1:{sock.getsockname()[1]}"}
        completed = subprocess.run(["node", "frontend/tests/agent-v2-browser.mjs", str(folder)],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        (folder / "navegador-agente-v2.txt").write_text(completed.stdout + completed.stderr, encoding="utf-8")
        print(completed.stdout + completed.stderr)
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
