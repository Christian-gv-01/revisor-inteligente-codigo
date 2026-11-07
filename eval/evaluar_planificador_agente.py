"""Evaluación A/B de UNA decisión del planificador de CODEGUARD.

Ruff y Bandit siempre se ejecutan para ambos grupos. El único tratamiento es
permitir o no que Gemini vea su resumen en la inspección AST inicial.
No ejecuta jamás el código evaluado; NO prueba el dictamen RAG ni la cobertura.
No persiste código, claves, errores crudos ni motivos del proveedor.

Ejecución de validación (sin Gemini):
    python eval/evaluar_planificador_agente.py

Ejecución real controlada:
    python eval/evaluar_planificador_agente.py --ejecutar --repeticiones 1
"""
from __future__ import annotations

import argparse
import ast
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import statistics
import sys
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.agente import (  # noqa: E402
    PasoAgente,
    SolicitudAgente,
    inspeccionar_estructura,
    planificar_gemini,
    resumen_estatico_planificador,
)
from app.services.llm import LLMError  # noqa: E402
from app.services.presupuesto import presupuesto_solicitud  # noqa: E402
from app.config import settings  # noqa: E402
from consumo_evaluacion import resumen_consumo  # noqa: E402
from app.services.static_analysis import ResultadoEstatico, analizar_estatico  # noqa: E402

CASOS_DEFECTO = ROOT / "eval" / "casos_planificador_agente.json"
SALIDA_DEFECTO = ROOT / "docs" / "evidencias" / "semana-4"
MAX_CASOS = 10
MAX_REPETICIONES = 3
MAX_CONSULTAS = 60
CONDICIONES = ("sin_contexto", "con_contexto")
CAMPOS_CSV = [
    "caso_id", "categoria", "repeticion", "orden", "condicion", "estado",
    "herramienta", "argumentos", "codigo_error", "latencia_ms", "sha256_codigo", "consumo_ia",
]


def cargar_casos(ruta: Path) -> list[dict]:
    datos = json.loads(ruta.read_text(encoding="utf-8-sig"))
    if not isinstance(datos, dict) or datos.get("version") != 1:
        raise ValueError("Versión del dataset A/B no compatible.")
    casos = datos.get("casos")
    if not isinstance(casos, list) or not 2 <= len(casos) <= MAX_CASOS:
        raise ValueError("Se requieren entre 2 y 10 casos de evaluación.")
    ids = set()
    salida = []
    for caso in casos:
        if not isinstance(caso, dict) or not all(
            isinstance(caso.get(campo), str) and caso[campo].strip()
            for campo in ("id", "categoria", "archivo", "codigo")
        ):
            raise ValueError("Caso incompleto o inválido.")
        ident = caso["id"]
        if not re.fullmatch(r"[a-z0-9_]{3,48}", ident) or ident in ids:
            raise ValueError("Identificador inválido o repetido.")
        ids.add(ident)
        solicitud = SolicitudAgente(
            archivo=caso["archivo"], codigo=caso["codigo"], max_pasos=3,
        )
        if "\x00" in solicitud.codigo:
            raise ValueError("El código no debe contener bytes nulos.")
        ast.parse(solicitud.codigo)  # Solo analiza sintaxis; nunca ejecuta.
        salida.append({
            "id": ident,
            "categoria": caso["categoria"][:48],
            "archivo": solicitud.archivo,
            "codigo": solicitud.codigo,
        })
    return salida


def ejecutar_pares(
    casos: list[dict],
    *,
    repeticiones: int = 1,
    version_herramientas: str = "1",
    pausa: float = 0,
    planificador: Callable = planificar_gemini,
    analizador_estatico: Callable = analizar_estatico,
    dormir: Callable[[float], None] = time.sleep,
    reloj: Callable[[], float] = time.monotonic,
) -> tuple[list[dict], list[dict]]:
    """Pares balanceados: mismo código, mismo AST; cambia solo el contexto.

    Los fallos de proveedor se conservan como fallos, nunca como una decisión.
    """
    if version_herramientas not in {"1", "2"}:
        raise ValueError("Versión del planificador no admitida.")
    if not 1 <= repeticiones <= MAX_REPETICIONES:
        raise ValueError("Las repeticiones deben estar entre 1 y 3.")
    if not 0 <= pausa <= 30:
        raise ValueError("La pausa debe estar entre 0 y 30 segundos.")
    if len(casos) * 2 * repeticiones > MAX_CONSULTAS:
        raise ValueError("El estudio excedería el límite de llamadas.")
    resultados: list[dict] = []
    exclusiones: list[dict] = []
    orden_total = 0

    for indice, caso in enumerate(casos):
        try:
            estatico: ResultadoEstatico = analizador_estatico(
                caso["codigo"], caso["archivo"],
            )
        except Exception as error:
            exclusiones.append({
                "caso_id": caso["id"],
                "motivo": "fallo_al_ejecutar_estatico",
                "tipo": type(error).__name__,
            })
            continue
        if estatico.estado != "completo":
            exclusiones.append({
                "caso_id": caso["id"],
                "motivo": "ruff_bandit_no_completados",
                "estado": estatico.estado,
            })
            continue

        estructura = inspeccionar_estructura(caso["codigo"])
        if not estructura.get("sintaxis_valida"):
            exclusiones.append({
                "caso_id": caso["id"], "motivo": "ast_no_disponible",
            })
            continue
        resumen = resumen_estatico_planificador(estatico)
        for repeticion in range(1, repeticiones + 1):
            # Alternancia AB/BA para no dar siempre ventaja al primer grupo.
            orden = (
                CONDICIONES if (indice + repeticion) % 2
                else tuple(reversed(CONDICIONES))
            )
            for condicion in orden:
                resultado = dict(estructura)
                if condicion == "con_contexto":
                    resultado["evidencia_ruff_bandit"] = resumen
                paso = PasoAgente(
                    numero=1,
                    herramienta="inspeccionar_estructura",
                    motivo="Inspección inicial de estructura.",
                    resultado=resultado,
                    origen="automatico",
                )
                orden_total += 1
                fila = {
                    "caso_id": caso["id"],
                    "categoria": caso["categoria"],
                    "repeticion": repeticion,
                    "orden": orden_total,
                    "condicion": condicion,
                    "estado": "ok",
                    "herramienta": None,
                    "codigo_error": None,
                    "latencia_ms": 0.0,
                    "sha256_codigo": sha256(caso["codigo"].encode()).hexdigest()[:16],
                }
                inicio = reloj()
                consumo = None
                try:
                    with presupuesto_solicitud(*settings.limites_solicitud("/api/v1/agente/analizar")) as consumo:
                        decision = (planificador(caso["codigo"], [paso], version_herramientas="2")
                                    if version_herramientas == "2" else planificador(caso["codigo"], [paso]))
                    fila["herramienta"] = decision.herramienta
                    fila["argumentos"] = decision.argumentos.model_dump()
                except LLMError as error:
                    fila["estado"] = "error_proveedor"
                    fila["codigo_error"] = error.codigo
                except Exception as error:
                    # Evitar filtrar código, mensajes HTTP, tokens o datos privados.
                    fila["estado"] = "error_inesperado"
                    fila["codigo_error"] = type(error).__name__
                finally:
                    fila["latencia_ms"] = round((reloj() - inicio) * 1000, 2)
                    fila["consumo_ia"] = consumo.consumo.publico() if consumo is not None else None
                resultados.append(fila)
                if pausa and orden_total < len(casos) * 2 * repeticiones:
                    dormir(pausa)

    return resultados, exclusiones


def resumen_estudio(resultados: list[dict], exclusiones: list[dict]) -> dict:
    pares: dict[tuple, dict] = {}
    for fila in resultados:
        pares.setdefault((fila["caso_id"], fila["repeticion"]), {})[
            fila["condicion"]
        ] = fila

    evaluados = []
    no_comparables = 0
    for (caso, repeticion), par in sorted(pares.items()):
        a = par.get("sin_contexto")
        b = par.get("con_contexto")
        if not a or not b or a["estado"] != "ok" or b["estado"] != "ok":
            no_comparables += 1
            continue
        evaluados.append({
            "caso_id": caso,
            "repeticion": repeticion,
            "sin_contexto": a["herramienta"],
            "con_contexto": b["herramienta"],
            "argumentos_sin_contexto": a.get("argumentos", {}),
            "argumentos_con_contexto": b.get("argumentos", {}),
            "cambio": (a["herramienta"], a.get("argumentos", {})) != (b["herramienta"], b.get("argumentos", {})),
        })
    cambios = sum(item["cambio"] for item in evaluados)
    condiciones = {}
    for condicion in CONDICIONES:
        filas = [f for f in resultados if f["condicion"] == condicion]
        validas = [f for f in filas if f["estado"] == "ok"]
        decisiones: dict[str, int] = {}
        for fila in validas:
            k = str(fila["herramienta"])
            decisiones[k] = decisiones.get(k, 0) + 1
        condiciones[condicion] = {
            "solicitudes": len(filas),
            "exitos": len(validas),
            "errores": len(filas) - len(validas),
            "tasa_exito": round(len(validas) / len(filas), 4) if filas else None,
            "latencia_media_ms_exitos": round(
                statistics.mean(f["latencia_ms"] for f in validas), 2,
            ) if validas else None,
            "distribucion_decisiones": decisiones,
            "consumo_ia": resumen_consumo(filas),
            "finalizaciones_en_primera_decision": sum(f["herramienta"] == "finalizar" for f in validas),
            "tasa_finalizacion_inicial_sobre_total": sum(f["herramienta"] == "finalizar" for f in validas) / len(filas) if filas else None,
        }
    return {
        "total_solicitudes": len(resultados),
        "casos_excluidos": exclusiones,
        "pares_completos": len(evaluados),
        "pares_no_comparables": no_comparables,
        "pares_con_cambio": cambios,
        "tasa_cambio_de_decision": round(cambios / len(evaluados), 4)
        if evaluados else None,
        "condiciones": condiciones,
        "pares": evaluados,
        "advertencia": (
            "Un cambio de herramienta NO demuestra mayor precisión ni "
            "mejor detección de vulnerabilidades. Se mide una decisión de "
            "planificación, sin ejecutar el informe Gemini + RAG. Los errores "
            "de proveedor se excluyen de las comparaciones, no son aciertos."
        ),
    }


def guardar(
    resultados: list[dict], resumen: dict, *, salida: Path, metadatos: dict,
) -> Path:
    salida.mkdir(parents=True, exist_ok=True)
    archivo_json = salida / "resultados.json"
    archivo_csv = salida / "resultados.csv"
    archivo_md = salida / "resumen.md"
    archivo_json.write_text(
        json.dumps({
            "metadatos": metadatos,
            "resumen": resumen,
            "solicitudes": resultados,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with archivo_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v
                          for k, v in fila.items()} for fila in resultados)
    with archivo_md.open("w", encoding="utf-8") as f:
        f.write("# Evaluación A/B del planificador de CODEGUARD\n\n")
        f.write(f"Modelo: `{metadatos['modelo']}`. Casos sintéticos: {metadatos['casos']}.\n\n")
        f.write(f"Solicitudes: {resumen['total_solicitudes']} · Pares completos: {resumen['pares_completos']} · Pares no comparables: {resumen['pares_no_comparables']}.\n\n")
        f.write(f"Cambios observados: {resumen['pares_con_cambio']} · Tasa de cambio: {resumen['tasa_cambio_de_decision']}.\n\n")
        f.write("| Caso | Repetición | Sin contexto | Argumentos A | Con contexto | Argumentos B | Cambio |\n")
        f.write("|---|---:|---|---|---|---|---|\n")
        for p in resumen["pares"]:
            f.write(
                f"| {p['caso_id']} | {p['repeticion']} | "
                f"{p['sin_contexto']} | {json.dumps(p['argumentos_sin_contexto'], ensure_ascii=False)} | "
                f"{p['con_contexto']} | {json.dumps(p['argumentos_con_contexto'], ensure_ascii=False)} | "
                f"{'Sí' if p['cambio'] else 'No'} |\n"
            )
        f.write("\n**Limitación:** " + resumen["advertencia"] + "\n")
    return archivo_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--casos", type=Path, default=CASOS_DEFECTO)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument("--version-herramientas", choices=("1", "2"), default="2")
    parser.add_argument("--pausa", type=float, default=0.75)
    parser.add_argument("--ejecutar", action="store_true",
                        help="Autoriza explícitamente las llamadas reales a Gemini.")
    parser.add_argument("--salida", type=Path, default=None)
    args = parser.parse_args()
    casos = cargar_casos(args.casos)
    if not 1 <= args.repeticiones <= MAX_REPETICIONES:
        parser.error("--repeticiones debe estar entre 1 y 3.")
    consultas = len(casos) * 2 * args.repeticiones
    if consultas > MAX_CONSULTAS:
        parser.error("Cantidad de llamadas superior al límite.")
    if not 0 <= args.pausa <= 30:
        parser.error("--pausa debe estar entre 0 y 30 segundos.")
    print(f"Casos: {len(casos)} · Repeticiones: {args.repeticiones} · Máximo de solicitudes: {consultas}.")
    print("Experimento: mismas muestras y AST; Ruff/Bandit se ejecuta en ambos grupos.")
    if not args.ejecutar:
        print("MODO SEGURO: dataset válido, ninguna solicitud realizada a Gemini.")
        print("Para ejecutar el A/B: agregue --ejecutar. Se requieren Ruff, Bandit y GEMINI_API_KEY.")
        return 0

    if args.salida is not None and args.salida.exists():
        parser.error("La salida existe; conservar las corridas anteriores.")

    marca = datetime.now(timezone.utc)
    resultados, excluidos = ejecutar_pares(
        casos, repeticiones=args.repeticiones, pausa=args.pausa, version_herramientas=args.version_herramientas,
    )
    resumen = resumen_estudio(resultados, excluidos)
    salida = args.salida or (
        SALIDA_DEFECTO / ("agente-ab-" + marca.strftime("%Y%m%dT%H%M%SZ"))
    )
    metadatos = {
        "fecha_utc": marca.isoformat(),
        "modelo": os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite",
        "casos": len(casos),
        "repeticiones": args.repeticiones,
        "version_herramientas": args.version_herramientas,
        "dataset_sha256": sha256(args.casos.read_bytes()).hexdigest(),
        "evaluador_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "diseño": "Pares AB/BA contrabalanceados; primera decisión únicamente.",
        "codigo_fuente_almacenado": False,
        "proveedor_simulado": False,
    }
    archivo = guardar(resultados, resumen, salida=salida, metadatos=metadatos)
    print(f"Solicitudes realizadas: {resumen['total_solicitudes']}.")
    print(f"Pares válidos: {resumen['pares_completos']}; no comparables: {resumen['pares_no_comparables']}.")
    print(f"Decisiones distintas: {resumen['pares_con_cambio']}.")
    print(f"Resumen y CSV/JSON disponibles en: {archivo.parent}")
    if not resumen["pares_completos"]:
        print("ADVERTENCIA: sin pares comparables; no extraer conclusiones.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
