"""Valida la traza v2 sin importar la aplicación ni sus servicios de IA.

Solo verifica el contrato observable; no certifica cobertura ni pertinencia RAG.
"""
from collections import Counter
import math
from urllib.parse import urlsplit

VERSION = "2"
AST = {"inspeccionar_estructura", "detectar_llamadas_sensibles", "revisar_consultas_sql"}
CONTEXTUALES = {"ampliar_contexto", "buscar_referencia"}
CATEGORIAS = {"ejecucion_codigo", "inyeccion_sql", "inyeccion_comandos", "inyeccion", "credenciales", "rutas", "deserializacion"}
TERMINACIONES = {"finalizacion_anticipada", "max_pasos", "herramienta_repetida"}


def entero(v, minimo, maximo):
    return type(v) is int and minimo <= v <= maximo


def texto(v, limite, vacio=False):
    return isinstance(v, str) and len(v) <= limite and (vacio or bool(v.strip()))


def argumentos(nombre, datos):
    if not isinstance(datos, dict):
        raise ValueError("Argumentos no estructurados")
    if nombre == "ampliar_contexto":
        valido = set(datos) == {"linea"} and entero(datos["linea"], 1, 12000)
    elif nombre == "buscar_referencia":
        valido = set(datos) == {"categoria"} and isinstance(datos["categoria"], str) and datos["categoria"] in CATEGORIAS
    else:
        valido = nombre in AST | {"finalizar"} and not datos
    if not valido:
        raise ValueError("Argumentos incompatibles con herramienta")
    return datos


def firma(nombre, args):
    return nombre, tuple(sorted(args.items()))


def resultado_contextual(nombre, args, resultado, codigo):
    if nombre == "ampliar_contexto":
        lineas = codigo.splitlines()
        linea = args["linea"]
        inicio, fin = max(1, linea - 6), min(len(lineas), linea + 6)
        esperadas = [{"numero": n, "texto": lineas[n - 1][:500], "truncada": len(lineas[n - 1]) > 500}
                     for n in range(inicio, fin + 1)]
        items = resultado.get("lineas")
        if any(type(resultado.get(k)) is not int for k in ("linea_objetivo", "linea_inicio", "linea_fin")) or not isinstance(items, list) or any(not isinstance(item, dict) or type(item.get("numero")) is not int or type(item.get("truncada")) is not bool for item in items):
            raise ValueError("Tipos de ventana incompatibles")
        if linea > len(lineas) or resultado != {"linea_objetivo": linea, "linea_inicio": inicio, "linea_fin": fin, "lineas": esperadas}:
            raise ValueError("Ventana no corresponde al código")
    else:
        if set(resultado) != {"categoria", "fragmentos"} or resultado["categoria"] != args["categoria"]:
            raise ValueError("Categoría incompatible")
        fragmentos = resultado["fragmentos"]
        if not isinstance(fragmentos, list) or len(fragmentos) > 2:
            raise ValueError("Cantidad de fragmentos incompatible")
        ids = set()
        for f in fragmentos:
            if not isinstance(f, dict) or f.get("area") != "seguridad" or not texto(f.get("id"), 160) or f["id"] in ids or not texto(f.get("texto"), 2000):
                raise ValueError("Fragmento incompatible")
            ids.add(f["id"])
            if any(not texto(f.get(k, ""), 300, vacio=True) for k in ("documento", "seccion", "fuente")):
                raise ValueError("Metadatos fuera de límites")
            url = f.get("url", "")
            if not texto(url, 2048, vacio=True):
                raise ValueError("URL incompatible")
            if url:
                u = urlsplit(url)
                if u.scheme != "https" or u.hostname not in {"cwe.mitre.org", "cheatsheetseries.owasp.org", "owasp.org", "www.owasp.org"} or u.username or u.password or u.port not in (None, 443) or "\\" in url or any(ord(c) <= 32 or ord(c) == 127 for c in url):
                    raise ValueError("URL fuera del contrato")
            distancia = f.get("distancia")
            if distancia is not None and (type(distancia) not in (int, float) or not math.isfinite(distancia)):
                raise ValueError("Distancia incompatible")


def validar_traza(caso, valor, *, max_pasos=3):
    if not isinstance(valor, dict) or valor.get("archivo") != caso["archivo"] or valor.get("version_herramientas") != VERSION:
        raise ValueError("El evaluador requiere agente v2")
    modo, fase = valor.get("modo"), valor.get("fase_error")
    if modo not in {"gemini_real", "degradado"} or fase not in {None, "planificacion", "informe", "herramienta"} or (modo == "gemini_real" and fase is not None):
        raise ValueError("Modo o fase incompatible")
    pasos, decisiones = valor.get("pasos"), valor.get("decisiones")
    if valor.get("max_pasos") != max_pasos or type(valor.get("max_pasos")) is not int or not isinstance(pasos, list) or not 1 <= len(pasos) <= max_pasos or not isinstance(decisiones, list) or len(decisiones) > max_pasos - 1:
        raise ValueError("Límites de traza incompatibles")
    ejecutadas = []
    vistos = {firma("inspeccionar_estructura", {})}
    for n, p in enumerate(pasos, 1):
        if not isinstance(p, dict) or type(p.get("numero")) is not int or p["numero"] != n or not texto(p.get("motivo"), 500) or p.get("herramienta") not in AST | CONTEXTUALES or not isinstance(p.get("resultado"), dict):
            raise ValueError("Paso incompatible")
        nombre, resultado = p["herramienta"], p["resultado"]
        origen = p.get("origen")
        if n == 1 and (nombre != "inspeccionar_estructura" or origen != "automatico"):
            raise ValueError("Inspección inicial incompatible")
        if n > 1 and origen not in {"gemini", "local"}:
            raise ValueError("Origen incompatible")
        if origen == "local" and (modo != "degradado" or nombre not in AST):
            raise ValueError("Respaldo local incompatible")
        args = argumentos(nombre, p.get("argumentos", {}))
        if nombre in CONTEXTUALES:
            if origen != "gemini":
                raise ValueError("Herramienta contextual atribuida a origen incorrecto")
            resultado_contextual(nombre, args, resultado, caso["codigo"])
        elif type(resultado.get("sintaxis_valida")) is not bool:
            raise ValueError("Resultado AST incompatible")
        if origen == "gemini":
            f = firma(nombre, args)
            if f in vistos:
                raise ValueError("Paso duplicado con mismos argumentos")
            vistos.add(f)
            ejecutadas.append(f)
    decisiones_ejecutadas = []
    firmas_previas = {firma("inspeccionar_estructura", {})}
    final = None
    errores = 0
    for n, d in enumerate(decisiones, 1):
        if not isinstance(d, dict) or type(d.get("numero")) is not int or d["numero"] != n or not texto(d.get("motivo"), 240) or d.get("estado") not in {"ejecutada", "finalizar", "repetida", "error"}:
            raise ValueError("Decisión incompatible")
        nombre, estado = d.get("herramienta"), d["estado"]
        args = argumentos(nombre, d.get("argumentos", {}))
        f = firma(nombre, args)
        if final is not None:
            raise ValueError("Decisiones después de terminar")
        if estado == "ejecutada":
            if nombre == "finalizar" or f in firmas_previas:
                raise ValueError("Decisión ejecutada incompatible")
            firmas_previas.add(f)
            decisiones_ejecutadas.append(f)
        else:
            final = estado
            if (estado == "finalizar") != (nombre == "finalizar"):
                raise ValueError("Finalización incompatible")
            if estado == "repetida" and f not in firmas_previas:
                raise ValueError("Repetición sin antecedente")
            if estado == "error":
                errores += 1
                if modo != "degradado" or fase != "herramienta":
                    raise ValueError("Error de herramienta sin degradación")
    if ejecutadas != decisiones_ejecutadas:
        raise ValueError("Decisiones y ejecuciones no corresponden")
    terminacion = valor.get("terminacion")
    if terminacion not in TERMINACIONES | {None}:
        raise ValueError("Terminación incompatible")
    esperado = "finalizacion_anticipada" if final == "finalizar" else "herramienta_repetida" if final == "repetida" else "max_pasos" if len(pasos) == max_pasos and modo == "gemini_real" else None
    if (modo == "gemini_real" and (terminacion is None or esperado != terminacion)) or (terminacion == "finalizacion_anticipada" and final != "finalizar") or (terminacion == "herramienta_repetida" and final != "repetida"):
        raise ValueError("Terminación no respaldada por decisiones")
    if fase == "herramienta" and errores != 1:
        raise ValueError("Fase de herramienta sin decisión fallida")
    return {"modo": modo, "version_herramientas": VERSION, "fase_error": fase,
            "pasos": len(pasos), "decisiones": len(decisiones), "terminacion": terminacion,
            "pasos_modelo": sum(p["origen"] == "gemini" for p in pasos),
            "pasos_automaticos": sum(p["origen"] == "automatico" for p in pasos),
            "pasos_respaldo": sum(p["origen"] == "local" for p in pasos),
            "herramientas_ejecutadas": dict(Counter(p["herramienta"] for p in pasos if p["origen"] == "gemini")),
            "decisiones_error": errores,
            "finalizacion_temprana": terminacion == "finalizacion_anticipada"}
