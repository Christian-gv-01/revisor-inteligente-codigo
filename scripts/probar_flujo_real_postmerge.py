"""Smoke público de agente y correcciones con proveedor real; nunca ejecuta código."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from pruebas_produccion import ClienteQA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--commit-servidor", required=True)
    parser.add_argument("--esperar-matriz", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Usa otra salida para conservar las evidencias.")
    if args.esperar_matriz:
        while not args.esperar_matriz.exists():
            time.sleep(5)
        # Otra corrida usó el mismo presupuesto por IP; respetar su última ventana.
        for _ in range(3):
            time.sleep(21)
    root = Path(__file__).resolve().parents[1]
    request = json.loads((root / "docs/contrato-confirmacion-v1/01-previsualizar-solicitud.json").read_text())
    cases = []
    result = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
              "commit_servidor_verificado": args.commit_servidor, "proveedor": "real mediante servidor",
              "casos": cases, "codigo_ejecutado": False, "original_sobrescrito": False,
              "nota": "Sesión HTTP, sin cookies en evidencia; no activa la interfaz de correcciones en producción."}
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def record(name, response, valid):
        cases.append({"caso": name, "http_status": response.status_code, "aprobado": bool(valid)})
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(name, response.status_code, bool(valid), flush=True)

    with ClienteQA(base_url=args.base_url, timeout=100, follow_redirects=False, trust_env=True) as client:
        response = client.post("/api/v1/agente/analizar", json={"archivo": request["archivo"], "codigo": request["codigo_original"], "max_pasos": 3})
        agent = response.json()
        result["respuesta_agente"] = agent
        report = agent.get("informe", {})
        record("Agente real: decisiones, informe y citas", response,
               response.status_code == 200 and agent.get("modo") == "gemini_real" and bool(agent.get("pasos"))
               and bool(agent.get("decisiones")) and bool(report.get("hallazgos")) and bool(report.get("fuentes")))
        for decision in ("aprobar", "rechazar"):
            response = client.post("/api/v1/correcciones/previsualizar", json=request)
            candidate = response.json()
            valid = response.status_code == 200 and candidate.get("sha256_original") == request["sha256_original"]
            if valid:
                code = candidate["codigo_propuesto"]
                valid = hashlib.sha256(code.encode()).hexdigest() == candidate["sha256_propuesto"] and code != request["codigo_original"]
                try:
                    ast.parse(code)
                except SyntaxError:
                    valid = False
            record("Previsualización real para " + decision, response, valid)
            if not valid:
                continue
            result["propuesta_" + decision] = candidate
            payload = {"decision": decision, "sha256_original": candidate["sha256_original"], "sha256_propuesto": candidate["sha256_propuesto"]}
            path = "/api/v1/correcciones/" + candidate["propuesta_id"] + "/decision"
            if decision == "aprobar":
                foreign = client.post(path, json=payload, headers={"Cookie": ""})
                record("Sin sesión: no permite decidir", foreign, foreign.status_code == 404)
            response = client.post(path, json=payload)
            value = response.json()
            valid = response.status_code == 200 and value.get("estado") == ("aprobada" if decision == "aprobar" else "rechazada")
            if decision == "aprobar":
                valid = valid and value.get("contenido") == candidate["codigo_propuesto"] and value.get("sha256_contenido") == candidate["sha256_propuesto"]
            else:
                valid = valid and "contenido" not in value
            record("Decisión real: " + decision, response, valid)
            if decision == "aprobar":
                repeated = client.post(path, json=payload)
                record("Aprobación idempotente: contenido idéntico", repeated, repeated.status_code == 200 and repeated.json() == value)
            opposite = client.post(path, json={**payload, "decision": "rechazar" if decision == "aprobar" else "aprobar"})
            record("Decisión opuesta: conflicto", opposite, opposite.status_code == 409)
    result["total"] = len(cases)
    result["aprobados"] = sum(c["aprobado"] for c in cases)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(result["aprobados"], "/", result["total"], flush=True)


if __name__ == "__main__":
    main()
