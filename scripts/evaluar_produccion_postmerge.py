"""Evalúa los 20 casos congelados contra una URL, sin ejecutar sus fragmentos.

Registra respuestas parciales y errores sin convertirlos en aciertos. El
presupuesto público se respeta mediante el mismo cliente de la matriz HTTP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from run_eval import load_cases, provenance, retrieval_metrics, analysis_metrics, summarize, validate_response, write_report
from pruebas_produccion import ClienteQA


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", required=True)
    p.add_argument("--commit-servidor", required=True, help="SHA verificado por separado en el despliegue")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error("La carpeta de salida ya existe; conservar las evidencias anteriores.")
    dataset = ROOT / "eval/preguntas_referencia.json"
    cases = load_cases(dataset)
    report = {**provenance(dataset), "modo": "api", "k": 3, "casos": [],
              "commit_servidor_verificado": args.commit_servidor,
              "configuracion": {"base_url": args.base_url, "proveedor": "real, mediante servidor desplegado",
                                "timeout_cliente_segundos": 100, "modelo_y_parametros_efectivos": "no expuestos por API",
                                "endpoint": "/api/v1/analizar", "agente_evaluado": False},
              "politica": "20 solicitudes, sin reintentos del evaluador; código sintético tratado como texto"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = args.output.parent / (args.output.name + "-checkpoint.json")
    with ClienteQA(base_url=args.base_url, timeout=100, follow_redirects=False) as c:
        health = c.get("/health")
        schema = c.get("/openapi.json")
        report["precondiciones"] = {"fecha_utc": datetime.now(timezone.utc).isoformat(),
            "health_status": health.status_code, "health": health.json(),
            "openapi_status": schema.status_code, "esquema_sha256": hashlib.sha256(schema.content).hexdigest(),
            "correcciones_disponibles": "/api/v1/correcciones/previsualizar" in schema.json().get("paths", {})}
        if health.status_code != 200 or not report["precondiciones"]["correcciones_disponibles"]:
            raise RuntimeError("Servidor no listo o versión anterior; no consumir Gemini.")
        for case in cases:
            row = {"id": case["id"], "nombre": case["nombre"]}
            started = time.perf_counter()
            try:
                response = c.post("/api/v1/analizar", json={"archivo": case["archivo"], "codigo": case["codigo"]})
                row["http_status"] = response.status_code
                if response.status_code != 200:
                    row.update(estado_ejecucion="error", error=f"HTTP {response.status_code}")
                else:
                    value = response.json()
                    row["respuesta"] = value
                    if value.get("estado") == "parcial":
                        row.update(estado_ejecucion="parcial", error="Sin informe generativo completo; evidencia estática conservada")
                    else:
                        validate_response(value, case)
                        metrics = retrieval_metrics([s["id"] for s in value.get("fuentes", [])], case["referencias_esperadas"], 3)
                        metrics.update(analysis_metrics(case, value))
                        row.update(estado_ejecucion="ok", metricas=metrics)
            except Exception as error:
                row.update(estado_ejecucion="error", error=type(error).__name__ + ": sin respuesta evaluable")
            row["duracion_ms"] = round((time.perf_counter() - started) * 1000, 2)
            report["casos"].append(row)
            checkpoint.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            print(f"{case['id']}: {row['estado_ejecucion']}; HTTP {row.get('http_status')}; {row['duracion_ms']} ms", flush=True)
        final_schema = c.get("/openapi.json")
        report["openapi_estable_al_final"] = hashlib.sha256(final_schema.content).hexdigest() == report["precondiciones"]["esquema_sha256"]
    report["resumen"] = summarize(report["casos"], "api")
    report["resumen"]["respuestas_parciales"] = sum(r["estado_ejecucion"] == "parcial" for r in report["casos"])
    report["resumen"]["nota"] = "Errores incluye respuestas parciales; métricas de calidad solo sobre informes completos. No equivale a evaluar el planificador del agente."
    write_report(args.output, report)
    print(json.dumps(report["resumen"], ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
