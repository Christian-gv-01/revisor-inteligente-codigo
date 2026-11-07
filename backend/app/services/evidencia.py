
"""Evidencia tipada y acotada; las reglas de herramientas no son citas RAG."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.static_analysis import ResultadoEstatico
from app.services.herramientas_contextuales import (
    ResultadoContexto,
    ResultadoReferencia,
)
from app.config import settings
from app.services.severidad import derivar_severidad, identificar_regla


class DatoEvidencia(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IndicadorEvidencia(DatoEvidencia):
    linea: int = Field(ge=1, le=12000)
    detalle: str = Field(min_length=1, max_length=160)


class InspeccionEvidencia(DatoEvidencia):
    herramienta: Literal[
        "inspeccionar_estructura",
        "detectar_llamadas_sensibles",
        "revisar_consultas_sql",
    ]
    origen: Literal["automatico", "gemini", "local"]
    sintaxis_valida: bool
    indicadores: list[IndicadorEvidencia] = Field(
        default_factory=list,
        max_length=20,
    )


class ReglaEvidencia(DatoEvidencia):
    id: str = Field(max_length=80)
    herramienta: Literal["ruff", "bandit"]
    regla: str = Field(min_length=1, max_length=40)
    linea: int = Field(ge=1, le=12000)
    columna: int | None = Field(default=None, ge=1)

    # Severidad original informada por la herramienta.
    severidad: Literal["critica", "alta", "media", "baja"]

    # Confianza original informada por Bandit.
    # Ruff no proporciona este dato.
    confianza: Literal["alta", "media", "baja"] | None = Field(
        default=None,
        exclude_if=lambda v: v is None,
    )

    # Severidad calculada por reglas deterministas del backend.
    severidad_derivada: Literal["critica", "alta", "media", "baja"]

    @model_validator(mode="before")
    @classmethod
    def calcular_severidad_derivada(cls, valores):
        if not isinstance(valores, dict):
            return valores

        datos = dict(valores)
        datos["id"] = identificar_regla(datos.get("herramienta"), datos.get("regla"), datos.get("linea"), datos.get("columna"))
        datos["severidad_derivada"] = derivar_severidad(
            datos.get("herramienta"),
            datos.get("severidad"),
            datos.get("confianza"),
        )
        return datos


class VinculoReglaContexto(DatoEvidencia):
    """Asociación verificable entre una regla y un contexto ampliado."""

    herramienta: Literal["ruff", "bandit"]
    id_regla: str = Field(max_length=80)
    regla: str = Field(min_length=1, max_length=40)

    linea_regla: int = Field(ge=1, le=12000)
    linea_objetivo: int = Field(ge=1, le=12000)
    linea_inicio: int = Field(ge=1, le=12000)
    linea_fin: int = Field(ge=1, le=12000)

    severidad_original: Literal["critica", "alta", "media", "baja"]
    confianza: Literal["alta", "media", "baja"] | None = Field(
        default=None,
        exclude_if=lambda v: v is None,
    )
    severidad_derivada: Literal["critica", "alta", "media", "baja"]

    @model_validator(mode="after")
    def validar_vinculo(self):
        if not self.linea_inicio <= self.linea_regla <= self.linea_fin:
            raise ValueError(
                "La línea de la regla debe pertenecer a la ventana contextual."
            )

        if not self.linea_inicio <= self.linea_objetivo <= self.linea_fin:
            raise ValueError(
                "La línea objetivo debe pertenecer a la ventana contextual."
            )

        return self


class EvidenciaRevision(DatoEvidencia):
    archivo: str = Field(min_length=4, max_length=255)

    inspecciones: list[InspeccionEvidencia] = Field(
        max_length=3,
    )

    estado_estatico: Literal[
        "completo",
        "parcial",
        "no_disponible",
    ]

    reglas: list[ReglaEvidencia] = Field(
        max_length=40,
    )

    vinculos_reglas_contexto: list[VinculoReglaContexto] = Field(
        default_factory=list,
        max_length=40,
        exclude_if=lambda v: not v,
    )

    total_reglas: int = Field(
        ge=0,
        le=400,
    )

    contextos_ampliados: list[ResultadoContexto] = Field(
        default_factory=list,
        max_length=3,
        exclude_if=lambda v: not v,
    )

    referencias_buscadas: list[ResultadoReferencia] = Field(
        default_factory=list,
        max_length=3,
        exclude_if=lambda v: not v,
    )



def vincular_reglas_contextuales(
    reglas: list[ReglaEvidencia],
    contextos: list[ResultadoContexto],
) -> list[VinculoReglaContexto]:
    """Registra cobertura de ventanas; no autoriza herencia de severidad."""

    vinculos = []
    vistos = set()

    for contexto in contextos:
        for regla in reglas:
            if not contexto.linea_inicio <= regla.linea <= contexto.linea_fin:
                continue

            clave = (
                regla.id,
                contexto.linea_objetivo,
                contexto.linea_inicio,
                contexto.linea_fin,
            )

            if clave in vistos:
                continue

            vistos.add(clave)

            vinculos.append(
                VinculoReglaContexto(
                    id_regla=regla.id,
                    herramienta=regla.herramienta,
                    regla=regla.regla,
                    linea_regla=regla.linea,
                    linea_objetivo=contexto.linea_objetivo,
                    linea_inicio=contexto.linea_inicio,
                    linea_fin=contexto.linea_fin,
                    severidad_original=regla.severidad,
                    confianza=regla.confianza,
                    severidad_derivada=regla.severidad_derivada,
                )
            )

    return sorted(vinculos, key=lambda v: (v.id_regla, v.linea_objetivo, v.linea_inicio, v.linea_fin))[:40]


def construir_evidencia(
    archivo: str,
    pasos: list[dict],
    estatico: ResultadoEstatico,
) -> EvidenciaRevision:

    inspecciones = []
    contextos = []
    referencias = []

    for paso in pasos[:settings.MAX_PASOS_AGENTE]:
        resultado = paso["resultado"]

        if paso["herramienta"] == "ampliar_contexto":
            contextos.append(
                ResultadoContexto.model_validate(resultado)
            )
            continue

        if paso["herramienta"] == "buscar_referencia":
            referencias.append(
                ResultadoReferencia.model_validate(resultado)
            )
            continue

        inspecciones.append(
            InspeccionEvidencia(
                herramienta=paso["herramienta"],
                origen=paso["origen"],
                sintaxis_valida=bool(
                    resultado.get("sintaxis_valida")
                ),
                indicadores=[
                    IndicadorEvidencia(
                        linea=i["linea"],
                        detalle=i.get("llamada") or i.get("patron"),
                    )
                    for i in resultado.get("indicadores", [])[:20]
                ],
            )
        )

    prioridad = {
        "critica": 0,
        "alta": 1,
        "media": 2,
        "baja": 3,
    }

    reglas = sorted(
        estatico.hallazgos,
        key=lambda h: (
            prioridad[h.severidad],
            h.linea,
            h.regla,
        ),
    )

    reglas_evidencia = [
        ReglaEvidencia(
            herramienta=h.herramienta,
            regla=h.regla,
            linea=h.linea,
            severidad=h.severidad,
            confianza=h.confianza,
            columna=h.columna,
        )
        for h in reglas[:40]
    ]

    vinculos = vincular_reglas_contextuales(
        reglas_evidencia,
        contextos,
    )

    return EvidenciaRevision(
        archivo=archivo,
        inspecciones=inspecciones,
        estado_estatico=estatico.estado,
        total_reglas=len(reglas),
        reglas=reglas_evidencia,
        vinculos_reglas_contexto=vinculos,
        contextos_ampliados=contextos,
        referencias_buscadas=referencias,
    )


def consultas_por_evidencia(
    evidencia: EvidenciaRevision,
) -> list[str]:
    """Categorías conocidas, no URLs ni instrucciones generadas por el modelo."""

    reglas = {r.regla for r in evidencia.reglas}

    detalles = {
        i.detalle
        for p in evidencia.inspecciones
        for i in p.indicadores
    }

    consultas = []

    if "B608" in reglas or any(
        "SQL dinamico" in d for d in detalles
    ):
        consultas.append(
            "Prevención de inyección SQL consultas parametrizadas concatenación"
        )

    if reglas & {
        "B602",
        "B603",
        "B604",
        "B605",
        "B606",
        "B607",
        "B609",
    } or any(
        d.startswith(("subprocess.", "os."))
        for d in detalles
    ):
        consultas.append(
            "Prevención de inyección de comandos del sistema subprocess shell=True os.system"
        )

    if reglas & {"B307", "B102"} or detalles & {"eval", "exec"}:
        consultas.append(
            "Evitar eval exec con entradas no confiables ejecución de código Python"
        )

    if reglas & {"B105", "B106", "B107"}:
        consultas.append(
            "Prevenir exposición de credenciales secretos tokens contraseñas en código"
        )

    return consultas[:5]
