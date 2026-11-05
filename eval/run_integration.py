"""Integra frontend, FastAPI, RAG y evaluador por HTTP con el proveedor de IA simulado.

No mide la calidad de Gemini. No modifica el backend de producción ni su .env.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
from hashlib import sha256
import json
import logging
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

from run_eval import DEFAULT_DATA, load_cases, prepare_rag, provenance, request_analysis, validate_response

ROOT = Path(__file__).resolve().parents[1]
SQL_CODE = 'nombre = input("Nombre: ")\ncursor.execute("SELECT * FROM usuarios WHERE nombre = \'" + nombre + "\'")\n'


class FixtureClient:
    """Respuestas controladas únicamente para probar el transporte y las validaciones."""

    calls = 0

    def __init__(self, **_):
        self.models = self

    def close(self):
        pass

    def generate_content(self, *, contents, **_):
        FixtureClient.calls += 1
        from httpx import TimeoutException

        if "DATOS_NO_CONFIABLES_JSON:\n" not in contents:
            return SimpleNamespace(text=json.dumps({"herramienta": "finalizar", "motivo": "Inspección inicial suficiente para el caso controlado"}), usage_metadata=None)
        payload = json.loads(contents.split("DATOS_NO_CONFIABLES_JSON:\n", 1)[1])
        code = payload["codigo_python_no_confiable"]
        if "INTEGRACION_ERROR" in code:
            raise TimeoutException("Tiempo de espera simulado exclusivamente en integración")
        findings = []
        if "INTEGRACION_VACIO" not in code:
            line = next((index for index, text in enumerate(code.splitlines(), 1) if "SELECT" in text), None)
            if line is not None:
                refs = [] if "INTEGRACION_SIN_CITA" in code else ["inventada"] if "INTEGRACION_CITA_INVALIDA" in code else ["seguridad_python-002"]
                findings.append({
                    "linea": line, "severidad": "alta", "categoria": "Inyección SQL",
                    "titulo": "Consulta SQL de la prueba de integración",
                    "explicacion": "Respuesta controlada del proveedor simulado para probar el contrato.",
                    "correccion_sugerida": 'cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,))',
                    "referencias": refs,
                    "fragmento_codigo": code.splitlines()[line - 1].strip(),
                })
        return SimpleNamespace(text=json.dumps({"hallazgos": findings}), usage_metadata=None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--static-analysis", action="store_true", help="Activa Ruff/Bandit reales y verifica degradación parcial")
    args = parser.parse_args(argv)
    folder = args.output or ROOT / "docs/evidencias/semana-3" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-integracion")
    if folder.exists():
        parser.error("Usa una carpeta nueva para conservar las evidencias anteriores.")
    node = shutil.which("node")
    vitest = ROOT / "frontend/node_modules/vitest/vitest.mjs"
    if not node or not vitest.is_file():
        parser.error("Faltan Node.js o las dependencias del frontend. Ejecuta npm ci en frontend/.")
    folder = folder.resolve()
    folder.mkdir(parents=True)
    report = {**provenance(DEFAULT_DATA), "tipo": "integracion_http", "proveedor_ia": "simulado",
              "rag": "ChromaDB local real", "llamadas_externas_ia": 0,
              "aviso": "Estas pruebas verifican integración; no miden precisión, recall ni F1 de Gemini."}
    report["integracion_runner_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    report["github_fixture_sha256"] = sha256((ROOT / "eval/integration_github_fixture.py").read_bytes()).hexdigest()
    report["frontend_http_test_sha256"] = sha256((ROOT / "frontend/tests/integration-http.test.tsx").read_bytes()).hexdigest()
    FixtureClient.calls = 0
    server = None
    thread = None
    try:
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {
                "GEMINI_API_KEY": "fixture-local-sin-credencial-real", "GEMINI_MODEL": "fixture-integracion",
                "LLM_TIMEOUT_SECONDS": "3", "STATIC_ANALYSIS_ENABLED": "1" if args.static_analysis else "0",
                "RATE_LIMIT_ENABLED": "0", "CONCURRENCY_LIMIT_ENABLED": "0",
            }))
            sys.path.insert(0, str(ROOT / "backend"))
            from app.main import app
            import app.services.llm as llm
            import uvicorn
            from integration_github_fixture import install_github_fixture
            install_github_fixture(stack, SQL_CODE)
            report["github"] = "API externa simulada; lector, validación y rutas reales"
            report["analisis_estatico"] = "Ruff/Bandit reales" if args.static_analysis else "desactivado"

            # Se parchea solo el cliente externo; la consulta RAG, las validaciones,
            # las rutas y la serialización de FastAPI siguen siendo las reales.
            stack.enter_context(patch.object(llm.genai, "Client", FixtureClient))
            _, rag_config = prepare_rag()
            report["configuracion_rag"] = rag_config

            @app.middleware("http")
            async def mark_fixture(request, call_next):
                response = await call_next(request)
                response.headers["X-Integration-Provider"] = "stub"
                return response

            sock = stack.enter_context(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            sock.bind(("127.0.0.1", 0))
            sock.listen(128)
            port = sock.getsockname()[1]
            server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False))
            thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
            thread.start()
            def stop_server():
                server.should_exit = True
                thread.join(timeout=5)
            stack.callback(stop_server)
            deadline = time.monotonic() + 15
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(.05)
            if not server.started:
                raise RuntimeError("La API temporal de integración no inició")
            base = f"http://127.0.0.1:{port}"
            print("API temporal iniciada en loopback; proveedor simulado y RAG real.", flush=True)

            case = load_cases(DEFAULT_DATA)[0]
            response = request_analysis(case, base, 15)
            validate_response(response, case)
            if response["estado"] != "analizado" or not response["hallazgos"]:
                raise RuntimeError("El evaluador no recibió un informe con hallazgos")
            source_ids = {source["id"] for source in response.get("fuentes", [])}
            if not all(set(finding["referencias"]) <= source_ids for finding in response["hallazgos"]):
                raise RuntimeError("Las citas de la prueba no se resolvieron")
            report["evaluador_http"] = "aprobado: request_analysis y validate_response contra FastAPI"
            (folder / "respuesta-api-controlada.json").write_text(json.dumps({"proveedor_ia": "simulado", "respuesta": response}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            with tempfile.TemporaryDirectory(prefix="codeguard-integration-") as temporary:
                archive = Path(temporary) / "proyecto.zip"
                with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as file:
                    file.writestr("usuarios.py", SQL_CODE)
                    file.writestr("sin_cita.py", "# INTEGRACION_SIN_CITA\n" + SQL_CODE)
                partial_archive = Path(temporary) / "parcial.zip"
                with zipfile.ZipFile(partial_archive, "w", zipfile.ZIP_DEFLATED) as file:
                    file.writestr("fallo.py", "# INTEGRACION_ERROR\neval(user_input)\n")
                    file.writestr("segundo.py", "eval(user_input)\n")
                env = dict(os.environ)
                # Las credenciales ficticias no necesitan llegar al proceso frontend.
                for key in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"):
                    env.pop(key, None)
                env.update(INTEGRATION_API_BASE_URL=base, INTEGRATION_ZIP_PATH=str(archive), PYTHONIOENCODING="utf-8")
                env.update(INTEGRATION_PARTIAL_ZIP_PATH=str(partial_archive), INTEGRATION_STATIC_ANALYSIS="1" if args.static_analysis else "0")
                command = [node, str(vitest), "run", "tests/integration-http.test.tsx", "--reporter=json", f"--outputFile={folder / 'vitest-integracion.json'}"]
                completed = subprocess.run(command, cwd=ROOT / "frontend", env=env, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=90)
                (folder / "frontend-http.txt").write_text(completed.stdout + completed.stderr, encoding="utf-8")
                if (folder / "vitest-integracion.json").is_file():
                    results = json.loads((folder / "vitest-integracion.json").read_text(encoding="utf-8"))
                    report["pruebas_frontend_http"] = {key: results.get(key) for key in ("numTotalTests", "numPassedTests", "numFailedTests", "numPendingTests", "success")}
                if completed.returncode:
                    raise RuntimeError("Falló al menos una prueba HTTP; consultar frontend-http.txt")
            report["estado"] = "aprobado"
            report["respuestas_controladas_proveedor"] = FixtureClient.calls
    except Exception as error:
        report["estado"] = "error"
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        if server:
            server.should_exit = True
        if thread:
            thread.join(timeout=5)
        (folder / "resultado-integracion.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    print(f"Evidencias: {folder}")
    return 0 if report["estado"] == "aprobado" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    raise SystemExit(main())

