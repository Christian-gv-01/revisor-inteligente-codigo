"""Política operativa explícita; herencia solo por regla citada y línea exacta."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Iterable, Literal

import yaml

from app.config.priorizacion import ORDEN_SEVERIDAD

Severidad = Literal["critica", "alta", "media", "baja"]
Confianza = Literal["alta", "media", "baja"] | None
Herramienta = Literal["ruff", "bandit"]


@lru_cache(maxsize=1)
def politica_severidad():
    ruta = Path(__file__).resolve().parents[1] / "config" / "severidad.yaml"
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    severidades = set(ORDEN_SEVERIDAD)
    confianzas = {"alta", "media", "baja", "desconocida"}
    if not isinstance(datos, dict) or datos.get("version") != 1:
        raise ValueError("Política de severidad no compatible.")
    if set(datos.get("bandit", {})) != severidades or set(datos.get("ruff", {})) != severidades:
        raise ValueError("La política debe cubrir todas las severidades.")
    for fila in datos["bandit"].values():
        if set(fila) != confianzas or any(v not in severidades for v in fila.values()):
            raise ValueError("Matriz de confianza incompleta.")
    if any(v not in severidades for v in datos["ruff"].values()):
        raise ValueError("Política Ruff inválida.")
    return datos


def derivar_severidad(herramienta: Herramienta, severidad: Severidad, confianza: Confianza) -> Severidad:
    if severidad not in ORDEN_SEVERIDAD or herramienta not in {"ruff", "bandit"}:
        raise ValueError("Herramienta o severidad no reconocida.")
    tabla = politica_severidad()[herramienta]
    if herramienta == "ruff":
        return tabla[severidad]
    conocida = confianza if confianza in {"alta", "media", "baja"} else "desconocida"
    return tabla[severidad][conocida]


def identificar_regla(herramienta, regla, linea, columna=None):
    """Identidad estable de origen/ubicación, sin datos del modelo ni secretos."""
    contenido = json.dumps([herramienta, regla, linea, columna], ensure_ascii=False, separators=(",", ":"))
    return "estatica-" + hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def combinar_severidades(severidad_original: Severidad, severidades_vinculadas: Iterable[Severidad] = ()) -> Severidad:
    candidatas = [severidad_original, *severidades_vinculadas]
    if any(s not in ORDEN_SEVERIDAD for s in candidatas):
        raise ValueError("Existe una severidad no reconocida.")
    return min(candidatas, key=ORDEN_SEVERIDAD.__getitem__)


def heredar_severidad_contextual(hallazgos: Iterable, reglas: Iterable) -> list:
    """No usa proximidad, categoría ni orden de ventanas como autorización.

    Una regla debe estar citada por ID, ser ofrecida por el backend y coincidir
    con la línea ya validada del hallazgo. No inferir asociaciones multilínea.
    Las propiedades de auditoría siempre se reconstruyen desde evidencia real.
    """
    from app.models.analisis import HerenciaSeveridad

    ofrecidas, ambiguas = {}, set()
    for regla in reglas:
        anterior = ofrecidas.get(regla.id)
        if anterior is not None and anterior.model_dump() != regla.model_dump():
            ambiguas.add(regla.id)
        ofrecidas[regla.id] = regla
    resultado = []
    for hallazgo in hallazgos:
        ids = sorted({id for id in hallazgo.reglas_evidencia
                      if id in ofrecidas and id not in ambiguas and ofrecidas[id].linea == hallazgo.linea})
        aplicadas = [ofrecidas[id] for id in ids]
        traza = [HerenciaSeveridad(id=r.id, herramienta=r.herramienta, regla=r.regla,
                 linea=r.linea, columna=r.columna, severidad_original=r.severidad,
                 confianza=r.confianza, severidad_derivada=r.severidad_derivada) for r in aplicadas]
        resultado.append(hallazgo.model_copy(update={
            "severidad": combinar_severidades(hallazgo.severidad, [r.severidad_derivada for r in aplicadas]),
            "reglas_evidencia": ids,
            "severidad_original_modelo": hallazgo.severidad if ids else None,
            "herencia_severidad": traza,
        }, deep=True))
    return resultado
