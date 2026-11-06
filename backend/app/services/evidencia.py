"""Evidencia tipada y acotada; las reglas de herramientas no son citas RAG."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.services.static_analysis import ResultadoEstatico


class DatoEvidencia(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IndicadorEvidencia(DatoEvidencia):
    linea: int = Field(ge=1, le=12000)
    detalle: str = Field(min_length=1, max_length=160)


class InspeccionEvidencia(DatoEvidencia):
    herramienta: Literal["inspeccionar_estructura", "detectar_llamadas_sensibles", "revisar_consultas_sql"]
    origen: Literal["automatico", "gemini", "local"]
    sintaxis_valida: bool
    indicadores: list[IndicadorEvidencia] = Field(default_factory=list, max_length=20)


class ReglaEvidencia(DatoEvidencia):
    herramienta: Literal["ruff", "bandit"]
    regla: str = Field(min_length=1, max_length=40)
    linea: int = Field(ge=1, le=12000)
    severidad: Literal["critica", "alta", "media", "baja"]


class EvidenciaRevision(DatoEvidencia):
    archivo: str = Field(min_length=4, max_length=255)
    inspecciones: list[InspeccionEvidencia] = Field(max_length=3)
    estado_estatico: Literal["completo", "parcial", "no_disponible"]
    reglas: list[ReglaEvidencia] = Field(max_length=40)
    total_reglas: int = Field(ge=0, le=400)


def construir_evidencia(archivo: str, pasos: list[dict], estatico: ResultadoEstatico) -> EvidenciaRevision:
    inspecciones = []
    for paso in pasos[:3]:
        resultado = paso["resultado"]
        inspecciones.append(InspeccionEvidencia(
            herramienta=paso["herramienta"], origen=paso["origen"],
            sintaxis_valida=bool(resultado.get("sintaxis_valida")),
            indicadores=[IndicadorEvidencia(
                linea=i["linea"], detalle=i.get("llamada") or i.get("patron"),
            ) for i in resultado.get("indicadores", [])[:20]],
        ))
    prioridad = {"critica": 0, "alta": 1, "media": 2, "baja": 3}
    reglas = sorted(estatico.hallazgos, key=lambda h: (prioridad[h.severidad], h.linea, h.regla))
    return EvidenciaRevision(
        archivo=archivo, inspecciones=inspecciones, estado_estatico=estatico.estado,
        total_reglas=len(reglas), reglas=[ReglaEvidencia(
            herramienta=h.herramienta, regla=h.regla, linea=h.linea, severidad=h.severidad,
        ) for h in reglas[:40]],
    )


def consultas_por_evidencia(evidencia: EvidenciaRevision) -> list[str]:
    """Categorías conocidas, no URLs ni instrucciones generadas por el modelo."""
    reglas = {r.regla for r in evidencia.reglas}
    detalles = {i.detalle for p in evidencia.inspecciones for i in p.indicadores}
    consultas = []
    if "B608" in reglas or any("SQL dinamico" in d for d in detalles):
        consultas.append("Prevención de inyección SQL consultas parametrizadas concatenación")
    if reglas & {"B602", "B603", "B604", "B605", "B606", "B607", "B609"} or any(d.startswith(("subprocess.", "os.")) for d in detalles):
        consultas.append("Prevención de inyección de comandos del sistema subprocess shell=True os.system")
    if reglas & {"B307", "B102"} or detalles & {"eval", "exec"}:
        consultas.append("Evitar eval exec con entradas no confiables ejecución de código Python")
    if reglas & {"B105", "B106", "B107"}:
        consultas.append("Prevenir exposición de credenciales secretos tokens contraseñas en código")
    return consultas[:5]
