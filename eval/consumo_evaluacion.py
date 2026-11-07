"""Uso numérico declarado por el servidor; no certifica facturación del proveedor."""
import json

CABECERA_CONSUMO = "X-Codeguard-Consumo-IA"
TOKENS = ("tokens_entrada", "tokens_salida", "tokens_totales")


def leer_consumo(valor):
    if not isinstance(valor, str) or len(valor) > 2048:
        return None
    try:
        d = json.loads(valor)
    except (ValueError, TypeError):
        return None
    if not isinstance(d, dict) or set(d) != {"version", "intentos", "respuestas", "uso_completo", *TOKENS}:
        return None
    entero = lambda x: type(x) is int and 0 <= x <= 1_000_000_000
    if type(d["version"]) is not int or d["version"] != 1 or not all(entero(d[k]) for k in ("intentos", "respuestas")) or d["respuestas"] > d["intentos"]:
        return None
    if any(d[k] is not None and not entero(d[k]) for k in TOKENS):
        return None
    completo = all(d[k] is not None for k in TOKENS)
    if type(d["uso_completo"]) is not bool or d["uso_completo"] != completo:
        return None
    if d["intentos"] != d["respuestas"] and any(d[k] is not None for k in TOKENS):
        return None
    if d["intentos"] == 0 and any(d[k] != 0 for k in TOKENS):
        return None
    return d


def resumen_consumo(filas):
    datos = [f.get("consumo_ia") for f in filas]
    salida = {"solicitudes": len(filas), "solicitudes_con_telemetria": sum(d is not None for d in datos),
              "fuente": "Contadores SDK declarados por el servidor; no factura ni estimación de costo."}
    for campo in ("intentos", *TOKENS):
        conocidos = [d[campo] for d in datos if d is not None and d[campo] is not None]
        salida[campo] = sum(conocidos) if len(conocidos) == len(datos) else None
        salida[campo + "_solicitudes_con_dato"] = len(conocidos)
        salida[campo + "_suma_solo_conocidos"] = sum(conocidos)
    return salida
