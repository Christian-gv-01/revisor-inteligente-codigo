"""Navegador contra FastAPI y SQLite reales; Gemini y GitHub externos simulados.

Servidor temporal exclusivo en loopback; ningún control fixture entra en la app.
"""
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
from unittest.mock import patch
import zipfile

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
    from run_integration import FixtureClient, SQL_CODE
    from run_eval import prepare_rag
    from integration_github_fixture import install_github_fixture
    import uvicorn
    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, {
            "PROJECT_BUDGET_ENABLED": "1", "CORRECTIONS_COOKIE_SECURE": "0",
            "RATE_LIMIT_ENABLED": "0", "CONCURRENCY_LIMIT_ENABLED": "0",
            "STATIC_ANALYSIS_ENABLED": "1", "GEMINI_API_KEY": "fixture-sin-credencial-real",
            "GEMINI_MODEL": "fixture-integracion", "LLM_RETRY_ATTEMPTS": "2",
        }))
        from app.main import app
        from app.services import proyectos, correcciones, llm
        stack.enter_context(patch.object(proyectos, "DB_PATH", folder / "presupuestos.sqlite3"))
        stack.enter_context(patch.object(correcciones, "DB_PATH", folder / "correcciones.sqlite3"))
        stack.enter_context(patch.object(llm.genai, "Client", FixtureClient))
        install_github_fixture(stack, SQL_CODE)
        prepare_rag()
        FixtureClient.calls = 0
        with zipfile.ZipFile(folder / "caso.zip", "w") as z:
            z.writestr("uno.py", SQL_CODE)
            z.writestr("dos.py", SQL_CODE)

        @app.get("/__budget_fixture__/status")
        async def status():
            return {"proveedor": "simulado", "llamadas": FixtureClient.calls}

        @app.post("/__budget_fixture__/{identificador}/caducar")
        async def caducar(identificador: str):
            with proyectos.conexion() as db:
                db.execute("UPDATE proyectos SET caduca=0 WHERE id=?", (proyectos.huella(identificador),))
            return {"fixture": True}

        sock = stack.enter_context(socket.socket())
        sock.bind(("127.0.0.1", 0))
        sock.listen(128)
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        def stop():
            server.should_exit = True
            thread.join(timeout=5)
        stack.callback(stop)
        limite = time.monotonic() + 15
        while not server.started and thread.is_alive() and time.monotonic() < limite:
            time.sleep(.05)
        if not server.started:
            raise RuntimeError("No inició la API fixture.")
        env = {**os.environ, "CODEGUARD_DEV_API_TARGET": f"http://127.0.0.1:{port}"}
        completed = subprocess.run(["node", "frontend/tests/project-budget-browser.mjs", str(folder)],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=150)
        (folder / "navegador-presupuesto.txt").write_text(completed.stdout + completed.stderr, encoding="utf-8")
        print(completed.stdout + completed.stderr)
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
