"""Compara informes completos directo/agente sin ejecutar el código del dataset."""
from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import platform
from pathlib import Path
import re
import statistics
import time
from urllib.parse import urlsplit

import httpx

from run_eval import DEFAULT_DATA, analysis_metrics, load_cases, validate_response
from contrato_agente_evaluacion import VERSION, validar_traza
from consumo_evaluacion import CABECERA_CONSUMO, leer_consumo, resumen_consumo

RUTAS = {"directa": "/api/v1/analizar", "agente": "/api/v1/agente/analizar"}
PESOS = {"directa": 1, "agente": 3}
CONFIG_PUBLICA = {"modelo", "temperatura_sintesis", "max_tokens_sintesis", "timeout_llm_segundos",
                  "temperatura_planificador", "max_tokens_planificador", "timeout_planificador_ms",
                  "fuente_verificacion", "campos_no_verificados", "corpus_sha256", "prompt_sha256",
                  "intentos_llm", "plazo_directo_segundos", "plazo_agente_segundos", "distancia_max_rag", "estatico_directa_habilitado"}


def validar_config(config):
    if not isinstance(config, dict) or set(config) != CONFIG_PUBLICA:
        raise ValueError("Indica todos los campos públicos previstos; nunca claves ni credenciales")
    campos = CONFIG_PUBLICA - {"fuente_verificacion", "campos_no_verificados"}
    desconocidos = config["campos_no_verificados"]
    if not isinstance(desconocidos, list) or any(not isinstance(x, str) or x not in campos for x in desconocidos) or len(set(desconocidos)) != len(desconocidos):
        raise ValueError("Lista de campos no verificados incompatible")
    if not isinstance(config["fuente_verificacion"], str) or not config["fuente_verificacion"].strip():
        raise ValueError("Registrar procedencia de la configuración")
    for campo in campos:
        valor = config[campo]
        if valor is None:
            if campo not in desconocidos:
                raise ValueError("Identificar expresamente los valores no verificados")
            continue
        if campo in desconocidos:
            raise ValueError("Un valor desconocido debe registrarse como null")
        if campo.endswith("sha256"):
            valido = isinstance(valor, str) and re.fullmatch(r"[0-9a-f]{64}", valor)
        elif campo == "estatico_directa_habilitado":
            valido = type(valor) is bool
        elif campo == "intentos_llm":
            valido = type(valor) is int and 1 <= valor <= 3
        elif campo == "distancia_max_rag":
            valido = type(valor) in (int, float) and math.isfinite(valor) and 0 <= valor <= 2
        elif campo == "modelo":
            valido = isinstance(valor, str) and valor.strip() and valor != "VALOR_VERIFICADO"
        else:
            valido = type(valor) in (int, float) and math.isfinite(valor)
            if campo.startswith("temperatura"):
                valido = valido and 0 <= valor <= 2
            else:
                valido = valido and valor > 0
            if campo.startswith("max_tokens"):
                valido = valido and type(valor) is int
        if not valido:
            raise ValueError("Sustituir marcadores por valores públicos verificados o null declarado")
    if config["plazo_directo_segundos"] is not None and config["plazo_directo_segundos"] > 45:
        raise ValueError("El plazo directo excede el máximo de la revisión base")
    if config["plazo_agente_segundos"] is not None and config["plazo_agente_segundos"] > 150:
        raise ValueError("El plazo del agente excede el máximo de la revisión base")
    return config


def comprobar_esquema(esquema, *, max_pasos=None):
    """Solo compatibilidad del contrato público; no atestación del commit."""
    try:
        paths = esquema["paths"]
        if not set(RUTAS.values()).issubset(paths):
            raise ValueError("Faltan rutas")
        cuerpo = paths[RUTAS["agente"]]["post"]["requestBody"]["content"]["application/json"]["schema"]
        if "$ref" in cuerpo:
            referencia = cuerpo["$ref"]
            if not referencia.startswith("#/components/schemas/"):
                raise ValueError("Referencia no local")
            cuerpo = esquema["components"]["schemas"][referencia.split("/")[-1]]
        if VERSION not in cuerpo["properties"]["version_herramientas"].get("enum", []):
            raise ValueError("El servidor no anuncia soporte de agente v2")
        if max_pasos is not None and cuerpo["properties"]["max_pasos"].get("maximum", 0) < max_pasos:
            raise ValueError("El servidor no admite el máximo de pasos solicitado")
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Esquema público incompatible con agente v2") from error


def plan(casos):
    """Mismos datos; diez pares por cada orden en el dataset de veinte casos."""
    return [(caso, ruta) for n, caso in enumerate(casos)
            for ruta in (("directa", "agente") if n % 2 == 0 else ("agente", "directa"))]


class Presupuesto:
    def __init__(self, *, reloj=time.monotonic, dormir=time.sleep):
        self.reloj, self.dormir = reloj, dormir
        self.reservas = deque()

    def reservar(self, peso):
        if peso not in (1, 3):
            raise ValueError("Peso fuera del contrato de comparación")
        inicio = self.reloj()
        while True:
            ahora = self.reloj()
            while self.reservas and ahora - self.reservas[0][0] >= 61:
                self.reservas.popleft()
            if sum(p for _, p in self.reservas) + peso <= 10:
                self.reservas.append((ahora, peso))
                return round((ahora - inicio) * 1000, 2)
            self.dormir(min(30, max(.01, 61 - (ahora - self.reservas[0][0]))))


def interpretar(caso, ruta, valor, *, max_pasos_agente=3):
    informe = valor
    extra = {}
    if ruta == "agente":
        extra = validar_traza(caso, valor, max_pasos=max_pasos_agente)
        informe = valor.get("informe")
        if valor["modo"] == "degradado" and (not isinstance(informe, dict) or informe.get("estado") != "parcial"):
            raise ValueError("Degradación sin estado parcial")
    if not isinstance(informe, dict) or informe.get("estado") not in {"analizado", "abstenido", "parcial"}:
        raise ValueError("Informe incompatible")
    # El validador histórico admite analizado/abstenido. Para comprobar el formato
    # de un parcial se usa una copia; sus métricas mantienen el estado parcial.
    formato = {**informe, "estado": "analizado"} if informe["estado"] == "parcial" else informe
    validate_response(formato, caso)
    if any(type(f.get("linea")) is not int for f in informe["hallazgos"]):
        raise ValueError("Línea no entera")
    metricas = analysis_metrics(caso, informe)
    return {"estado_ejecucion": "parcial" if informe["estado"] == "parcial" else "completo",
            "estado_informe": informe["estado"], "metricas_observadas": metricas, **extra}


def evaluar(cliente, casos, *, presupuesto=None, checkpoint=None, max_pasos_agente=3):
    filas = []
    for caso, ruta in plan(casos):
        espera = presupuesto.reservar(PESOS[ruta]) if presupuesto else 0
        fila = {"id": caso["id"], "nombre": caso["nombre"], "ruta": ruta,
                "orden_global": len(filas) + 1, "espera_presupuesto_ms": espera}
        carga = {"archivo": caso["archivo"], "codigo": caso["codigo"]}
        if ruta == "agente":
            carga["max_pasos"] = max_pasos_agente
            carga["version_herramientas"] = VERSION
        inicio = time.perf_counter()
        try:
            respuesta = cliente.post(RUTAS[ruta], json=carga)
            fila["duracion_http_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
            fila["http_status"] = respuesta.status_code
            cabecera = respuesta.headers.get(CABECERA_CONSUMO)
            fila["consumo_ia"] = leer_consumo(cabecera)
            fila["estado_telemetria"] = "reportada" if fila["consumo_ia"] is not None else "no_disponible" if cabecera is None else "invalida"
            if respuesta.status_code != 200:
                fila.update(estado_ejecucion="error_http", error=f"HTTP {respuesta.status_code}; cuerpo omitido")
            else:
                try:
                    valor = respuesta.json()
                except ValueError:
                    fila.update(estado_ejecucion="error_json", error="Respuesta no JSON")
                else:
                    try:
                        fila.update(interpretar(caso, ruta, valor, max_pasos_agente=max_pasos_agente))
                    except (ValueError, KeyError, TypeError):
                        fila.update(estado_ejecucion="error_contrato", error="Respuesta incompatible con el evaluador")
                    # Solo cuerpos HTTP 200 del ejemplo sintético. Los errores del
                    # proveedor y sus cabeceras no se copian a la evidencia.
                    fila["respuesta"] = valor
        except httpx.HTTPError as error:
            fila.update(estado_ejecucion="error_transporte", error=type(error).__name__)
        fila.setdefault("duracion_http_ms", round((time.perf_counter() - inicio) * 1000, 2))
        filas.append(fila)
        if checkpoint:
            checkpoint(filas)
    return filas


def cociente(a, b):
    return a / b if b else None


def calidad(filas):
    totales = {k: sum(f["metricas_observadas"][k] for f in filas)
               for k in ("tp", "fp", "fn", "hallazgos", "hallazgos_con_citas_resueltas", "referencias", "referencias_resueltas", "lineas_fuera_rango")}
    tp, fp, fn = (totales[k] for k in ("tp", "fp", "fn"))
    return {**totales, "precision": cociente(tp, tp + fp), "recall": cociente(tp, tp + fn),
            "f1": cociente(2 * tp, 2 * tp + fp + fn),
            "cobertura_citas": cociente(totales["hallazgos_con_citas_resueltas"], totales["hallazgos"]),
            "validez_referencias": cociente(totales["referencias_resueltas"], totales["referencias"])}


def resumen(filas, casos):
    esperado = {c["id"] for c in casos}
    if len(filas) != 2 * len(casos) or Counter((f["id"], f["ruta"]) for f in filas) != Counter((c["id"], r) for c in casos for r in RUTAS):
        raise ValueError("La comparación necesita exactamente un resultado por caso y ruta")
    rutas = {}
    completos = {}
    for ruta in RUTAS:
        propias = [f for f in filas if f["ruta"] == ruta]
        validas = [f for f in propias if f["estado_ejecucion"] == "completo"]
        completos[ruta] = {f["id"] for f in validas}
        tiempos = sorted(f["duracion_http_ms"] for f in propias)
        aciertos = sum(f["metricas_observadas"]["acierto_caso"] for f in validas)
        rutas[ruta] = {"total": len(propias), "estados": dict(Counter(f["estado_ejecucion"] for f in propias)),
            "consumo_ia": resumen_consumo(propias), "completos": len(validas), "tasa_completitud": cociente(len(validas), len(casos)),
            "aciertos_completos": aciertos, "aciertos_sobre_total": cociente(aciertos, len(casos)),
            "calidad_solo_completos": calidad(validas), "abstenciones_completas": sum(f["estado_informe"] == "abstenido" for f in validas),
            "latencia_http_media_ms_todos": statistics.mean(tiempos) if tiempos else None,
            "latencia_http_p95_ms_todos": tiempos[math.ceil(.95 * len(tiempos)) - 1] if tiempos else None,
            "finalizaciones_tempranas": sum(f.get("finalizacion_temprana", False) for f in propias) if ruta == "agente" else None,
            "tasa_finalizacion_temprana_sobre_total": cociente(sum(f.get("finalizacion_temprana", False) for f in propias), len(propias)) if ruta == "agente" else None,
            "terminaciones": dict(Counter(f.get("terminacion") or "no_determinada" for f in propias if "modo" in f)) if ruta == "agente" else None,
            "fases_error": dict(Counter(f["fase_error"] for f in propias if f.get("fase_error"))) if ruta == "agente" else None,
            "decisiones_error": sum(f.get("decisiones_error", 0) for f in propias) if ruta == "agente" else None}
    comunes = completos["directa"] & completos["agente"]
    comparacion = {ruta: calidad([f for f in filas if f["ruta"] == ruta and f["id"] in comunes]) for ruta in RUTAS}
    latencias = {}
    for ruta in RUTAS:
        tiempos = sorted(f["duracion_http_ms"] for f in filas if f["ruta"] == ruta and f["id"] in comunes)
        latencias[ruta] = {"media_ms": statistics.mean(tiempos) if tiempos else None,
                          "p95_ms": tiempos[math.ceil(.95 * len(tiempos)) - 1] if tiempos else None}
    return {"rutas": rutas, "pares_completos": len(comunes), "ids_pares_completos": sorted(comunes),
            "ids_excluidos_de_comparacion_pareada": sorted(esperado - comunes),
            "calidad_en_mismos_pares_completos": comparacion,
            "latencia_http_en_mismos_pares_completos": latencias,
            "aviso": "Parciales y fallos permanecen en resultados y completitud; no se convierten en aciertos ni se mezclan con informes completos."}


def guardar(carpeta, informe):
    (carpeta / "resultados.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (carpeta / "resultados.csv").open("w", encoding="utf-8-sig", newline="") as out:
        claves = ["id", "ruta", "orden_global", "estado_ejecucion", "http_status", "duracion_http_ms", "espera_presupuesto_ms", "tp", "fp", "fn", "finalizacion_temprana", "version_herramientas", "terminacion", "fase_error", "decisiones_error", "tokens_entrada", "tokens_salida", "tokens_totales", "intentos", "estado_telemetria"]
        writer = csv.DictWriter(out, fieldnames=claves)
        writer.writeheader()
        for f in informe["casos"]:
            combinado = {**f, **f.get("metricas_observadas", {}), **(f.get("consumo_ia") or {})}
            writer.writerow({k: combinado.get(k) for k in claves})
    s = informe["resumen"]
    lineas = ["# Comparación de rutas", "", f"Revisión declarada por el operador: `{informe['revision_servidor_declarada']}`.",
        "", f"Esquema estable durante la corrida: {informe.get('esquema_estable')}. Si es falso, no tratar la comparación como una versión estable.",
        "", f"Pares con informe completo en ambas rutas: {s['pares_completos']} de {len(informe['casos']) // 2}.", "",
        "| Ruta | Completos | Aciertos / total | TP | FP | FN | Precisión | Recall | F1 |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for ruta, m in s["rutas"].items():
        q = s["calidad_en_mismos_pares_completos"][ruta]
        valores = [q[k] if q[k] is not None else "No calculable" for k in ("tp", "fp", "fn", "precision", "recall", "f1")]
        lineas.append(f"| {ruta} | {m['completos']} | {m['aciertos_sobre_total']} | " + " | ".join(map(str, valores)) + " |")
    lineas += ["", "TP/FP/FN y métricas de esta tabla usan únicamente los mismos pares completos. Los estados y latencias de todas las solicitudes están en JSON/CSV.",
        "", "Configuración pública completa declarada: " + str(informe.get("configuracion_completa_declarada")) + ". Si contiene valores no verificados, la corrida es exploratoria, no una comparación bajo configuración totalmente controlada.",
        "", "Una corrida pequeña no demuestra generalización ni causalidad. Las citas se resuelven por ID; su pertinencia y los parches requieren revisión humana.",
        "La revisión del servidor y su configuración son declaradas por el operador, no atestadas por OpenAPI. Igualdad del esquema no garantiza igualdad de código.",
        "El uso numérico procede de la cabecera del servidor y de los metadatos del SDK, no de una factura. Si falta algún contador o hay intentos sin respuesta, se conserva null; no inferir ahorro ni tokens desde el número de pasos. Cobertura y sumas parciales están en JSON."]
    (carpeta / "comparacion.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", type=Path, default=DEFAULT_DATA)
    p.add_argument("--validar", action="store_true", help="Comprueba dataset y orden sin hacer peticiones")
    p.add_argument("--ejecutar", action="store_true", help="Autoriza las 40 solicitudes del conjunto")
    p.add_argument("--base-url")
    p.add_argument("--revision-servidor")
    p.add_argument("--dataset-sha256")
    p.add_argument("--config-publica", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--timeout", type=float, default=190)
    p.add_argument("--max-pasos-agente", type=int, choices=(3, 4), default=4)
    p.add_argument("--usar-proxy-entorno", action="store_true")
    args = p.parse_args(argv)
    casos = load_cases(args.dataset)
    huella = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    if args.validar or not args.ejecutar:
        print(json.dumps({"casos": len(casos), "solicitudes_previstas": len(plan(casos)), "dataset_sha256": huella,
                          "orden": "alternado por caso; diez pares por cada orden", "llamadas_realizadas": 0, "version_herramientas_agente": VERSION, "max_pasos_agente": args.max_pasos_agente}, ensure_ascii=False, indent=2))
        return 0
    if not args.base_url or not args.output or not args.config_publica or not re.fullmatch(r"[0-9a-f]{40}", args.revision_servidor or ""):
        p.error("Indica URL, salida nueva, configuración pública y SHA completo verificado del servidor.")
    u = urlsplit(args.base_url)
    if u.scheme not in {"http", "https"} or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in {"", "/"}:
        p.error("Usa URL raíz HTTP(S), sin credenciales, consulta ni fragmento.")
    if u.scheme != "https" and u.hostname not in {"127.0.0.1", "localhost", "::1"}:
        p.error("Un servidor remoto requiere HTTPS")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        p.error("Timeout positivo y finito requerido")
    if args.dataset_sha256 != huella:
        p.error("El SHA-256 suministrado no coincide con el dataset congelado.")
    try:
        config = validar_config(json.loads(args.config_publica.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        p.error(str(error))
    if args.output.exists():
        p.error("La salida existe; conservar corridas anteriores.")
    informe = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "revision_servidor_declarada": args.revision_servidor,
        "configuracion_servidor_declarada": config, "dataset_sha256": huella,
        "configuracion_completa_declarada": not config["campos_no_verificados"],
        "configuracion_publica_sha256": hashlib.sha256(args.config_publica.read_bytes()).hexdigest(),
        "evaluador_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "validador_traza_sha256": hashlib.sha256(Path(__file__).with_name("contrato_agente_evaluacion.py").read_bytes()).hexdigest(),
        "metricas_sha256": hashlib.sha256(Path(__file__).with_name("run_eval.py").read_bytes()).hexdigest(),
        "python": platform.python_version(), "httpx": httpx.__version__,
        "version_herramientas_agente": VERSION,
        "base_url": args.base_url, "timeout_cliente_segundos": args.timeout, "max_pasos_agente": args.max_pasos_agente,
        "solicitudes_analisis_previstas": 40, "solicitudes_control_previstas": 3,
        "reintentos_evaluador": 0, "llamadas_gemini_observadas": None,
        "estimacion_maxima_llamadas_generativas_sin_reintentos_servidor": len(casos) * (1 + args.max_pasos_agente),
        "tope_intentos_proveedor_configuracion_base": {"directa": 3, "agente": 9, "total_cuarenta_solicitudes": 240},
        "aviso_consumo": "Topes verificados en la revisión base; declarar configuración efectiva. No son consumo observado ni una cotización.",
        "proveedor": "servidor HTTP; requiere verificar por separado que no es un fixture", "casos": []}
    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=args.timeout, trust_env=args.usar_proxy_entorno, follow_redirects=False) as cliente:
        salud, esquema = cliente.get("/health"), cliente.get("/openapi.json")
        if salud.status_code != 200 or esquema.status_code != 200:
            raise RuntimeError("Faltan salud o esquema; no iniciar consumo generativo.")
        comprobar_esquema(esquema.json(), max_pasos=args.max_pasos_agente)
        if salud.headers.get("X-Integration-Provider") == "stub":
            raise RuntimeError("Servidor marcado como fixture: no registrar como comparación real.")
        informe["esquema_inicial_sha256"] = hashlib.sha256(esquema.content).hexdigest()
        args.output.mkdir(parents=True)
        def checkpoint(filas):
            informe["casos"] = filas
            (args.output / "checkpoint.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            f = filas[-1]
            print(f"{f['id']} {f['ruta']}: {f['estado_ejecucion']}", flush=True)
        filas = evaluar(cliente, casos, presupuesto=Presupuesto(), checkpoint=checkpoint, max_pasos_agente=args.max_pasos_agente)
        try:
            fin = cliente.get("/openapi.json")
            informe["esquema_estable"] = fin.status_code == 200 and hashlib.sha256(fin.content).hexdigest() == informe["esquema_inicial_sha256"]
        except httpx.HTTPError:
            informe["esquema_estable"] = False
            informe["error_verificacion_final"] = "No se pudo comprobar el esquema al terminar; resultados conservados"
    informe["casos"], informe["resumen"] = filas, resumen(filas, casos)
    guardar(args.output, informe)
    print(f"Evidencias conservadas en {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
