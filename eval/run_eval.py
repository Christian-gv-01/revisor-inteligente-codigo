"""Evaluación reproducible de recuperación RAG y de la API. No ejecuta el código evaluado."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import json
import logging
import math
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = Path(__file__).with_name("preguntas_referencia.json")


def load_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    cases = data["casos"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("Se requiere una lista no vac?a de casos.")

    ids = [
        case.get("id")
        for case in cases
        if isinstance(case, dict)
    ]

    if len(ids) != len(cases) or any(
        not isinstance(case_id, str) or not case_id.strip()
        for case_id in ids
    ):
        raise ValueError("Cada caso debe tener un identificador no vac?o.")

    if len(set(ids)) != len(ids):
        raise ValueError("Los identificadores deben ser ?nicos.")

    for case in cases:
        for key in ("id", "nombre", "pregunta", "archivo", "codigo", "respuesta_referencia"):
            if not isinstance(case[key], str) or not case[key].strip():
                raise ValueError(f"Campo {key} inválido: {case['id']}")
        if len(case["codigo"]) > 12000 or not case["archivo"].endswith(".py"):
            raise ValueError(f"Entrada fuera del contrato: {case['id']}")
        ast.parse(case["codigo"])  # Solo sintaxis: nunca eval, exec ni import del fragmento.
        refs = case["referencias_esperadas"]
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x for x in refs):
            raise ValueError("Referencias esperadas inválidas")
        if len(set(refs)) != len(refs):
            raise ValueError("Referencias esperadas duplicadas")
        if case["estado_esperado"] not in ("analizado", "abstenido"):
            raise ValueError("Estado esperado inválido")
        for expected in case["hallazgos_esperados"]:
            re.compile(expected["patron"], re.I)
            if not expected["lineas"] or any(type(n) is not int or not 1 <= n <= len(case["codigo"].splitlines()) for n in expected["lineas"]):
                raise ValueError("Líneas esperadas inválidas")
    return cases


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def retrieval_metrics(ids: list[str], relevant: list[str], k: int) -> dict:
    # Un ID repetido no puede aumentar la puntuación.
    top = list(dict.fromkeys(ids))[:k]
    expected = set(relevant)
    hits = len(set(top) & expected)
    return {
        "precision_at_k": hits / k if expected else None,
        "recall_at_k": ratio(hits, len(expected)),
        "mrr_at_k": next((1 / rank for rank, ref in enumerate(top, 1) if ref in expected), 0.0) if expected else None,
        "hit_at_k": float(hits > 0) if expected else None,
        "sin_fuentes_fuera_cobertura": float(not top) if not expected else None,
    }


def validate_response(value: dict, case: dict) -> None:
    if not isinstance(value, dict) or value.get("archivo") != case["archivo"] or value.get("estado") not in ("analizado", "abstenido"):
        raise ValueError("Respuesta incompatible: archivo o estado")
    findings, sources = value.get("hallazgos"), value.get("fuentes", [])
    if not isinstance(findings, list) or not isinstance(sources, list):
        raise ValueError("Respuesta incompatible: listas")
    if value["estado"] == "abstenido" and findings:
        raise ValueError("Una abstención no puede contener hallazgos")
    ids = set()
    for source in sources:
        if not isinstance(source, dict) or not all(isinstance(source.get(k), str) for k in ("id", "documento", "seccion", "fuente", "url")) or not source["id"].strip():
            raise ValueError("Fuente inválida")
        if source["id"] in ids:
            raise ValueError("Fuente duplicada")
        ids.add(source["id"])
    for finding in findings:
        if not isinstance(finding, dict) or type(finding.get("linea")) is not int or finding["linea"] < 1:
            raise ValueError("Hallazgo sin línea válida")
        if finding.get("severidad") not in ("critica", "alta", "media", "baja") or not all(isinstance(finding.get(k), str) for k in ("categoria", "titulo", "explicacion", "correccion_sugerida")):
            raise ValueError("Hallazgo incompatible")
        refs = finding.get("referencias", [])
        if not isinstance(refs, list) or not all(isinstance(ref, str) and ref.strip() for ref in refs):
            raise ValueError("Referencias inválidas")


def analysis_metrics(case: dict, response: dict) -> dict:
    findings = response["hallazgos"]
    expected = case["hallazgos_esperados"]
    # Emparejamiento uno a uno: la categoría y una línea admisible deben coincidir.
    # Máximo emparejamiento para que el orden de los hallazgos no cambie el resultado.
    edges = [[i for i, f in enumerate(findings) if f["linea"] in e["lineas"] and re.search(e["patron"], f'{f["categoria"]} {f["titulo"]}', re.I)] for e in expected]
    matched = {}

    def assign(index, seen):
        for candidate in edges[index]:
            if candidate not in seen:
                seen.add(candidate)
                if candidate not in matched or assign(matched[candidate], seen):
                    matched[candidate] = index
                    return True
        return False

    tp = sum(assign(i, set()) for i in range(len(expected)))
    source_ids = {s["id"] for s in response.get("fuentes", [])}
    citations = [(f, list(dict.fromkeys(f.get("referencias", [])))) for f in findings]
    refs_count = sum(len(refs) for _, refs in citations)
    valid_refs = sum(ref in source_ids for _, refs in citations for ref in refs)
    grounded = sum(bool(refs) and all(ref in source_ids for ref in refs) for _, refs in citations)
    abstained = response["estado"] == "abstenido"
    return {
        "tp": tp, "fp": len(findings) - tp, "fn": len(expected) - tp,
        "abstenido": abstained,
        "acierto_caso": response["estado"] == case["estado_esperado"] and tp == len(expected) == len(findings),
        "hallazgos": len(findings), "hallazgos_con_citas_resueltas": grounded,
        "referencias": refs_count, "referencias_resueltas": valid_refs,
        "lineas_fuera_rango": sum(f["linea"] > len(case["codigo"].splitlines()) for f in findings),
    }


def average(rows: list[dict], key: str):
    values = [row["metricas"][key] for row in rows if row.get("metricas", {}).get(key) is not None]
    return statistics.mean(values) if values else None


def summarize(rows: list[dict], mode: str) -> dict:
    valid = [r for r in rows if r["estado_ejecucion"] == "ok"]
    latencies = sorted(r["duracion_ms"] for r in valid)
    summary = {"total": len(rows), "completados": len(valid), "errores": len(rows) - len(valid),
               "tasa_completitud": ratio(len(valid), len(rows)),
               "latencia_media_ms": statistics.mean(latencies) if latencies else None,
               "latencia_p95_ms": latencies[math.ceil(.95 * len(latencies)) - 1] if latencies else None}
    for key in ("precision_at_k", "recall_at_k", "mrr_at_k", "hit_at_k", "sin_fuentes_fuera_cobertura"):
        summary[key] = average(valid, key)
    summary["casos_con_referencias_esperadas_evaluados"] = sum(r["metricas"]["recall_at_k"] is not None for r in valid)
    if mode == "api":
        totals = {key: sum(r["metricas"][key] for r in valid) for key in ("tp", "fp", "fn", "hallazgos", "hallazgos_con_citas_resueltas", "referencias", "referencias_resueltas", "lineas_fuera_rango")}
        summary.update(totals)
        summary.update(precision=ratio(totals["tp"], totals["tp"] + totals["fp"]),
                       recall=ratio(totals["tp"], totals["tp"] + totals["fn"]),
                       f1=ratio(2 * totals["tp"], 2 * totals["tp"] + totals["fp"] + totals["fn"]),
                       cobertura_citas=ratio(totals["hallazgos_con_citas_resueltas"], totals["hallazgos"]),
                       validez_referencias=ratio(totals["referencias_resueltas"], totals["referencias"]),
                       tasa_abstencion=average(valid, "abstenido"),
                       exactitud_casos_validos=average(valid, "acierto_caso"),
                       aciertos_sobre_total=ratio(sum(r["metricas"]["acierto_caso"] for r in valid), len(rows)))
    return summary


def provenance(dataset: Path) -> dict:
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    except (OSError, subprocess.SubprocessError):
        revision, dirty = None, None
    versions = {}
    for package in ("chromadb", "google-genai", "fastapi", "pydantic"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {"fecha_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
            "commit_base": revision, "cambios_locales": dirty, "dependencias": versions,
            "dataset_sha256": digest(dataset), "runner_sha256": digest(Path(__file__)),
            "knowledge_sha256": digest(ROOT / "knowledge/seguridad_python.md"),
            "llm_sha256": digest(ROOT / "backend/app/services/llm.py"),
            "rag_sha256": digest(ROOT / "backend/app/services/rag.py")}


def prepare_rag():
    sys.path.insert(0, str(ROOT / "backend"))
    from app.services.llm import _construir_consulta_rag, _recuperar_contexto_rag
    from app.services.rag import DB_PATH, MAX_DISTANCE
    import chromadb
    if not DB_PATH.is_dir():
        raise RuntimeError("Falta data/chroma. Ejecutar scripts/ingest.py.")
    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        collection = client.get_collection("seguridad_python")
        count = collection.count()
        if not count:
            raise RuntimeError("La colección de seguridad está vacía")
        # Verifica también el motor de embeddings; el servicio LLM oculta estos errores.
        collection.query(query_texts=["seguridad Python"], n_results=1)
    finally:
        client.close()

    def retrieve(case):
        query = _construir_consulta_rag(case["codigo"])
        failures = []

        class CaptureFailures(logging.Handler):
            def emit(self, record):
                if record.getMessage().startswith("rag_unavailable"):
                    failures.append(record.getMessage())

        logger = logging.getLogger("app.services.llm")
        handler = CaptureFailures()
        logger.addHandler(handler)
        try:
            _, sources = _recuperar_contexto_rag(case["codigo"])
        finally:
            logger.removeHandler(handler)
        if failures:
            raise RuntimeError("Recuperación no disponible; no es una abstención válida")
        return {"consulta_transformada": query, "fuentes": sources}
    return retrieve, {"coleccion": "seguridad_python", "fragmentos": count, "distancia_maxima": MAX_DISTANCE,
                      "proveedor_ia_utilizado": False, "calentamiento_fuera_de_latencia": True}


def request_analysis(case: dict, base: str, timeout: float) -> dict:
    request = Request(base.rstrip("/") + "/api/v1/analizar",
                      data=json.dumps({"archivo": case["archivo"], "codigo": case["codigo"]}).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def write_report(folder: Path, report: dict) -> None:
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "resultados.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = report["casos"]
    with (folder / "resultados.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "nombre", "estado_ejecucion", "duracion_ms", "error", "precision_at_k", "recall_at_k", "mrr_at_k", "tp", "fp", "fn", "abstenido"])
        writer.writeheader()
        for row in rows:
            flattened = {**row, **row.get("metricas", {})}
            writer.writerow({key: flattened.get(key) for key in writer.fieldnames})
    lines = [f"# Evaluación {report['modo']}", "", f"Fecha UTC: {report['fecha_utc']}", "", "Las métricas nulas no se pudieron calcular. Los errores no son respuestas correctas.", "", "| Métrica | Valor |", "|---|---:|"]
    for key, value in report["resumen"].items():
        lines.append(f"| {key} | {value if value is not None else 'No disponible'} |")
    lines += ["", "## Casos", "", "| Caso | Estado | Tiempo (ms) | Error |", "|---|---|---:|---|"]
    for row in rows:
        error = row.get("error", "").replace("|", "/").replace("\n", " ")
        lines.append(f"| {row['id']} — {row['nombre']} | {row['estado_ejecucion']} | {row['duracion_ms']} | {error} |")
    (folder / "resumen.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("rag", "api"), default="rag")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.k < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("k y timeout deben ser positivos y finitos")
    url = urlsplit(args.base_url)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password or url.query or url.fragment:
        parser.error("Usa una URL HTTP(S) sin credenciales, parámetros ni fragmento")
    try:
        cases = load_cases(args.dataset)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        parser.error(str(error))
    if args.validate_only:
        print(f"Dataset válido: {len(cases)} preguntas; código comprobado sin ejecutarlo.")
        return 0
    output = args.output or ROOT / "docs/evidencias/semana-3" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + args.mode)
    if output.exists():
        parser.error("La carpeta de salida ya existe; utiliza otra para conservar las evidencias.")
    report = {**provenance(args.dataset), "modo": args.mode, "k": args.k, "casos": []}
    setup_error = None
    if args.mode == "rag":
        try:
            retrieve, config = prepare_rag()
            report["configuracion"] = config
        except Exception as error:
            setup_error = f"{type(error).__name__}: no se pudo preparar ChromaDB; verificar dependencias, ingesta y embeddings."
    else:
        report["configuracion"] = {"base_url": args.base_url, "timeout": args.timeout,
                                    "aviso": "La configuración y revisión del servidor deben registrarse por separado."}
    for case in cases:
        row = {"id": case["id"], "nombre": case["nombre"]}
        start = time.perf_counter()
        try:
            if setup_error:
                raise RuntimeError(setup_error)
            response = retrieve(case) if args.mode == "rag" else request_analysis(case, args.base_url, args.timeout)
            if args.mode == "api":
                validate_response(response, case)
            ids = [source["id"] for source in response.get("fuentes", [])]
            metrics = retrieval_metrics(ids, case["referencias_esperadas"], args.k)
            if args.mode == "api":
                metrics.update(analysis_metrics(case, response))
            row.update(estado_ejecucion="ok", metricas=metrics, respuesta=response)
        except HTTPError as error:
            row.update(estado_ejecucion="error", error=f"HTTP {error.code}")
        except (URLError, TimeoutError, ConnectionError):
            row.update(estado_ejecucion="error", error="Conexión fallida o tiempo de espera agotado")
        except Exception as error:
            # No guardar cuerpos de error del proveedor ni valores del entorno.
            row.update(estado_ejecucion="error", error=setup_error or f"{type(error).__name__}: respuesta o ejecución inválida")
        row["duracion_ms"] = round((time.perf_counter() - start) * 1000, 2)
        report["casos"].append(row)
        print(f"{case['id']}: {row['estado_ejecucion']} ({row['duracion_ms']} ms)", flush=True)
    report["resumen"] = summarize(report["casos"], args.mode)
    write_report(output, report)
    print(f"Evidencias: {output}")
    print(json.dumps(report["resumen"], ensure_ascii=False, indent=2))
    return 1 if report["resumen"]["errores"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
