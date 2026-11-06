
from typing import Literal

from pydantic import BaseModel, Field, PrivateAttr

from app.services.static_analysis import ResultadoEstatico


class SolicitudAnalisis(BaseModel):
    archivo: str = Field(min_length=1, max_length=255)
    codigo: str = Field(min_length=1, max_length=12000)


class Hallazgo(BaseModel):
    linea: int = Field(ge=1)
    severidad: Literal["critica", "alta", "media", "baja"]
    categoria: str
    titulo: str
    explicacion: str
    correccion_sugerida: str

    # Identificadores exactos de los fragmentos que respaldan
    # el hallazgo. Se validarán en el servicio LLM.
    referencias: list[str] = Field(default_factory=list)
    fragmento_codigo: str | None = Field(default=None, max_length=500, exclude_if=lambda v: v is None)
    linea_reportada_modelo: int | None = Field(default=None, ge=1, exclude_if=lambda v: v is None)


class Fuente(BaseModel):
    # Identificador del fragmento original de ChromaDB.
    id: str = ""

    documento: str = ""
    seccion: str = ""
    fuente: str = ""
    url: str = ""
    distancia: float | None = None


class InformeModelo(BaseModel):
    # Esquema estructurado que utiliza Gemini.
    hallazgos: list[Hallazgo]

    # NUEVO: estado y mensaje para gestionar la abstención.
    estado: Literal["analizado", "abstenido"] = "analizado"
    mensaje: str | None = None

    # Metadatos internos que no forman parte del JSON de Gemini.
    _fuentes: list[dict] = PrivateAttr(default_factory=list)
    _motivo_abstencion: str | None = PrivateAttr(default=None)
    _revision_parcial: str | None = PrivateAttr(default=None)

    @property
    def estado_validado(self) -> str:
        return "abstenido" if self._motivo_abstencion else "parcial" if self._revision_parcial else "analizado"

    @property
    def mensaje_validado(self) -> str | None:
        return self._motivo_abstencion or self._revision_parcial

    @property
    def fuentes(self) -> list[dict]:
        return self._fuentes

    @property
    def motivo_abstencion(self) -> str | None:
        return self._motivo_abstencion


class RespuestaAnalisis(BaseModel):
    archivo: str
    estado: Literal["analizado", "abstenido", "parcial"]
    hallazgos: list[Hallazgo]
    fuentes: list[Fuente] = Field(default_factory=list)
    # Independiente de las referencias RAG: Ruff/Bandit tienen sus propias reglas.
    # Se omite cuando está desactivado, para preservar los contratos anteriores.
    analisis_estatico: ResultadoEstatico | None = Field(
        default=None, exclude_if=lambda value: value is None
    )

    # Mensaje cuando no existe evidencia suficiente.
    mensaje: str | None = None


class RespuestaAnalisisZIP(BaseModel):
    archivo_zip: str
    estado: Literal["analizado", "parcial"]
    total_archivos: int = Field(ge=1)
    informes: list[RespuestaAnalisis]



class SolicitudGitHub(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class RespuestaAnalisisRepositorio(BaseModel):
    repositorio: str
    estado: Literal["analizado", "parcial"]
    total_archivos: int = Field(ge=1)
    informes: list[RespuestaAnalisis]


