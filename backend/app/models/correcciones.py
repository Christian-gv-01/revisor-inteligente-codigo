"""Modelos HTTP del flujo de corrección con confirmación humana."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ARCHIVO_RE = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9_.-]{0,115}\.py$")


def unidades_utf16(texto: str) -> int:
    """Cuenta unidades UTF-16, igual que String.length en JavaScript."""
    return len(texto.encode("utf-16-le")) // 2


class ObjetivoCorreccion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    linea: int = Field(ge=1)
    descripcion: str = Field(min_length=1, max_length=1000)


class SolicitudPrevisualizacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    archivo: str = Field(min_length=4, max_length=120)
    codigo_original: str = Field(min_length=1, max_length=12000)
    sha256_original: str = Field(pattern=_SHA256_RE.pattern)
    objetivo: ObjetivoCorreccion

    @model_validator(mode="after")
    def validar_entrada(self) -> "SolicitudPrevisualizacion":
        if not _ARCHIVO_RE.fullmatch(self.archivo) or ".." in self.archivo:
            raise ValueError("El archivo debe ser un nombre .py simple, sin rutas.")
        if "/" in self.archivo or "\\" in self.archivo or "\x00" in self.archivo:
            raise ValueError("El nombre del archivo no es válido.")
        if "\x00" in self.codigo_original:
            raise ValueError("El código original contiene un carácter NUL.")
        try:
            longitud = unidades_utf16(self.codigo_original)
        except UnicodeEncodeError as exc:
            raise ValueError("El código original contiene Unicode no válido.") from exc
        if longitud > 12000:
            raise ValueError("El código original supera 12000 unidades UTF-16.")
        return self


class SolicitudDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["aprobar", "rechazar"]
    sha256_original: str = Field(pattern=_SHA256_RE.pattern)
    sha256_propuesto: str = Field(pattern=_SHA256_RE.pattern)


class RespuestaPrevisualizacion(BaseModel):
    version: Literal["1"]
    propuesta_id: str
    estado: Literal["pendiente_confirmacion"]
    accion: Literal["descargar_copia"]
    archivo_original: str
    archivo_salida: str
    sha256_original: str
    sha256_propuesto: str
    codigo_propuesto: str
    caduca_en: str
    advertencias: list[str] = Field(max_length=10)
