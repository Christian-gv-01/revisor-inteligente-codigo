
from typing import Literal

from pydantic import BaseModel, Field


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


class InformeModelo(BaseModel):
    hallazgos: list[Hallazgo]


class RespuestaAnalisis(BaseModel):
    archivo: str
    estado: Literal["analizado"]
    hallazgos: list[Hallazgo]

class RespuestaAnalisisZIP(BaseModel):
    archivo_zip: str
    estado: Literal["analizado"]
    total_archivos: int = Field(ge=1)
    informes: list[RespuestaAnalisis]

